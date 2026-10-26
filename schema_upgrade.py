"""Small, repeatable SQLite upgrade for existing student-project databases."""

from sqlalchemy import inspect, text


def upgrade_existing_database(db):
    inspector = inspect(db.engine)
    if "users" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("users")}
    additions = {
        "display_name": "VARCHAR(80)",
        "role": "VARCHAR(10) NOT NULL DEFAULT 'user'",
        "is_active_account": "BOOLEAN NOT NULL DEFAULT 1",
        "session_version": "INTEGER NOT NULL DEFAULT 0",
        "last_login_at": "DATETIME",
        "failed_login_count": "INTEGER NOT NULL DEFAULT 0",
        "login_blocked_until": "DATETIME",
    }
    with db.engine.begin() as connection:
        for name, definition in additions.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN {name} {definition}"))
        if "health_analyses" in inspector.get_table_names():
            analysis_columns = {column["name"] for column in inspector.get_columns("health_analyses")}
            if "weekly_plan" not in analysis_columns:
                connection.execute(text("ALTER TABLE health_analyses ADD COLUMN weekly_plan JSON"))
