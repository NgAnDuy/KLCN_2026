"""Authorization and ownership checks against an isolated database."""

import os
import sys
import unittest
from pathlib import Path
from flask import g
from sqlalchemy import create_engine, inspect, text
from tempfile import TemporaryDirectory

os.environ["HEALTH_DATABASE_URI"] = "sqlite:///:memory:"
test_state_dir = TemporaryDirectory()
os.environ["HEALTH_SERVER_STATE_FILE"] = str(Path(test_state_dir.name) / "server_state.json")
os.environ["HEALTH_DISABLE_HEARTBEAT"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app, db, SERVER_SESSION_ID  # noqa: E402
from models import AuditLog, HealthAnalysis, HealthProfile, User  # noqa: E402
from schema_upgrade import upgrade_existing_database  # noqa: E402


class AuthAdminTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.context = app.app_context()
        self.context.push()
        db.drop_all()
        db.create_all()
        self.admin = User(username="admin", role="admin")
        self.admin.set_password("admin-pass-123")
        self.alice = User(username="alice", role="user")
        self.alice.set_password("alice-pass-123")
        self.bob = User(username="bob", role="user")
        self.bob.set_password("bob-pass-123")
        db.session.add_all([self.admin, self.alice, self.bob])
        db.session.commit()
        self.record = HealthAnalysis(
            user_id=self.bob.id, selected_goal="maintenance",
            predicted_goal="maintenance", confidence=0.8,
            input_data={"weight_kg": 70},
            result_data={"health_status": {"items": []}, "recommendations": {}},
        )
        db.session.add(self.record)
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def token(self):
        with self.client.session_transaction() as data:
            return data["csrf_token"]

    def login(self, username, password):
        g.pop("_login_user", None)
        self.client.get("/login")
        response = self.client.post("/login", data={
            "csrf_token": self.token(), "username": username, "password": password,
        })
        self.client.get(response.headers["Location"])
        return response

    def test_register_cannot_choose_admin(self):
        self.client.get("/register")
        response = self.client.post("/register", data={
            "csrf_token": self.token(), "username": "newuser",
            "password": "password123", "confirm_password": "password123",
            "role": "admin",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.query.filter_by(username="newuser").one().role, "user")

    def test_user_cannot_read_admin_pages_or_another_result(self):
        self.login("alice", "alice-pass-123")
        self.assertEqual(self.client.get("/admin").status_code, 403)
        self.assertEqual(self.client.get(f"/history/{self.record.id}").status_code, 404)
        self.assertEqual(self.client.get(f"/admin/analyses/{self.record.id}").status_code, 403)

    def test_admin_views_data_and_audit_log(self):
        self.record.result_data = {
            "health_status": {"items": []},
            "recommendations": {
                "summary": ["Personalized guidance"],
                "foods": [{"food_name": "Oatmeal", "calories": 180,
                           "protein_g": 6, "carbs_g": 30, "fat_g": 3,
                           "reason": "Good fiber content"}],
                "exercises": [{"exercise_name": "Walking", "duration_min": 30,
                               "intensity": "low", "difficulty": "easy",
                               "reason": "Suitable activity"}],
            },
        }
        db.session.commit()
        self.login("admin", "admin-pass-123")
        page = self.client.get(f"/admin/analyses/{self.record.id}")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"70", page.data)
        self.assertIn(b"Personalized guidance", page.data)
        self.assertIn(b"Oatmeal", page.data)
        self.assertIn(b"Walking", page.data)
        self.assertNotIn(b'"food_name"', page.data)
        self.assertNotIn(b'"exercise_name"', page.data)
        self.assertEqual(AuditLog.query.filter_by(action="view_analysis").count(), 1)

    def test_lock_revokes_existing_user_session(self):
        alice_client = app.test_client()
        alice_client.get("/login")
        with alice_client.session_transaction() as data:
            token = data["csrf_token"]
        alice_client.post("/login", data={"csrf_token": token,
                                            "username": "alice", "password": "alice-pass-123"})
        self.login("admin", "admin-pass-123")
        response = self.client.post(f"/admin/users/{self.alice.id}/status",
                                    data={"csrf_token": self.token()})
        self.assertEqual(response.status_code, 302)
        g.pop("_login_user", None)
        self.assertEqual(alice_client.get("/account").status_code, 302)
        self.assertFalse(db.session.get(User, self.alice.id).is_active_account)

    def test_post_requires_csrf(self):
        self.client.get("/register")
        self.assertEqual(self.client.post("/register", data={"username": "test"}).status_code, 400)

    def test_profile_prefills_only_owners_health_form(self):
        db.session.add(HealthProfile(user_id=self.alice.id, data={
            "weight_kg": 62, "selected_goal": "maintenance",
        }))
        db.session.commit()
        self.login("alice", "alice-pass-123")
        self.assertIn(b'value="62"', self.client.get("/health").data)
        self.client.post("/logout", data={"csrf_token": self.token()})
        self.login("bob", "bob-pass-123")
        self.assertNotIn(b'value="62"', self.client.get("/health").data)

    def test_legacy_user_table_upgrade_keeps_existing_rows(self):
        engine = create_engine("sqlite:///:memory:")
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(80), password_hash VARCHAR(255))"))
            connection.execute(text("INSERT INTO users VALUES (1, 'legacy', 'stored-hash')"))
            connection.execute(text("CREATE TABLE health_analyses (id INTEGER PRIMARY KEY, user_id INTEGER)"))
        legacy_db = type("LegacyDB", (), {"engine": engine})()
        upgrade_existing_database(legacy_db)
        upgrade_existing_database(legacy_db)
        columns = {column["name"] for column in inspect(engine).get_columns("users")}
        self.assertTrue({"display_name", "role", "is_active_account", "session_version", "last_login_at",
                         "failed_login_count", "login_blocked_until"} <= columns)
        self.assertIn("weekly_plan", {column["name"] for column in inspect(engine).get_columns("health_analyses")})
        with engine.connect() as connection:
            self.assertEqual(connection.execute(text("SELECT username, role FROM users")).one(),
                             ("legacy", "user"))

    def test_analysis_flow_saves_profile_and_history(self):
        self.login("alice", "alice-pass-123")
        values = {
            "csrf_token": self.token(), "display_name": "Alice Demo",
            "goal": "maintenance", "age": "30",
            "gender": "Male", "height_cm": "170", "weight_kg": "70",
            "activity_level": "Moderate", "calories_consumed": "2100",
            "avg_steps_7d": "7000", "avg_sleep_hours_7d": "7",
            "water_intake_l": "2", "avg_exercise_minutes_7d": "30",
            "exercise_sessions_7d": "3", "avg_calories_burned_7d": "200",
        }
        response = self.client.post("/health", data=values)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(db.session.get(User, self.alice.id).display_name, "Alice Demo")
        self.assertEqual(HealthProfile.query.filter_by(user_id=self.alice.id).one().data["age"], 30)
        self.client.get("/analyzing")
        result = self.client.post("/process-analysis", data={"csrf_token": self.token()})
        self.assertEqual(result.status_code, 302)
        self.assertEqual(HealthAnalysis.query.filter_by(user_id=self.alice.id).count(), 1)
        self.assertEqual(HealthProfile.query.filter_by(user_id=self.alice.id).one().data["weight_kg"], 70.0)
        weekly_page = self.client.get("/weekly-plan")
        self.assertEqual(weekly_page.status_code, 200)
        self.assertIn(b"weekly_plan.css", weekly_page.data)
        self.assertIsNotNone(HealthAnalysis.query.filter_by(user_id=self.alice.id).one().weekly_plan)

    def test_basic_profile_remains_after_new_analysis_and_new_login(self):
        self.login("alice", "alice-pass-123")
        values = {
            "csrf_token": self.token(), "display_name": "Alice Smith",
            "goal": "maintenance", "age": "31", "gender": "Female",
            "height_cm": "165", "weight_kg": "62", "activity_level": "Light",
            "calories_consumed": "1800", "avg_steps_7d": "6000",
            "avg_sleep_hours_7d": "8", "water_intake_l": "2",
            "avg_exercise_minutes_7d": "20", "exercise_sessions_7d": "3",
            "avg_calories_burned_7d": "150",
        }
        self.assertEqual(self.client.post("/health", data=values).status_code, 302)
        self.assertEqual(self.client.get("/new-analysis").status_code, 302)
        self.client.post("/logout", data={"csrf_token": self.token()})
        self.login("alice", "alice-pass-123")
        page = self.client.get("/health").data
        for expected in (b'value="Alice Smith"', b'value="31"', b'value="165.0"', b'value="62.0"',
                         b'value="Female" selected'):
            self.assertIn(expected, page)
        profile_page = self.client.get("/profile")
        self.assertEqual(profile_page.status_code, 200)
        self.assertIn(b"Alice Smith", profile_page.data)

    def test_five_failed_logins_temporarily_block_account(self):
        self.client.get("/login")
        token = self.token()
        for _ in range(5):
            response = self.client.post("/login", data={
                "csrf_token": token, "username": "alice", "password": "wrong-pass",
            })
            self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(db.session.get(User, self.alice.id).login_blocked_until)
        response = self.client.post("/login", data={
            "csrf_token": token, "username": "alice", "password": "alice-pass-123",
        })
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
