
from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)


# ============================================================
# DATABASE INSTANCE
# ============================================================

db = SQLAlchemy()


# ============================================================
# USER MODEL
# ============================================================

class User(UserMixin, db.Model):
    """Store user account information."""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    analyses = db.relationship(
        "HealthAnalysis",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # --------------------------------------------------------
    # PASSWORD SECURITY
    # --------------------------------------------------------

    def set_password(self, password):
        """Hash and store a password securely."""

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):
        """Verify a password against its stored hash."""

        return check_password_hash(
            self.password_hash,
            password,
        )

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"


# ============================================================
# HEALTH ANALYSIS MODEL
# ============================================================

class HealthAnalysis(db.Model):
    """Store health inputs and analysis results per user."""

    __tablename__ = "health_analyses"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    selected_goal = db.Column(
        db.String(50),
        nullable=False,
    )

    predicted_goal = db.Column(
        db.String(50),
        nullable=False,
    )

    confidence = db.Column(
        db.Float,
        nullable=False,
    )

    input_data = db.Column(
        db.JSON,
        nullable=False,
    )

    result_data = db.Column(
        db.JSON,
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship(
        "User",
        back_populates="analyses",
    )

    def __repr__(self):
        return (
            f"<HealthAnalysis id={self.id} "
            f"user_id={self.user_id} "
            f"goal={self.predicted_goal}>"
        )
