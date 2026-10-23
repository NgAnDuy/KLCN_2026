
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from models import User, db


auth_blueprint = Blueprint("auth", __name__)


AUTH_MESSAGES = {
    "vi": {
        "username_length": "Tên đăng nhập phải có từ 3 đến 80 ký tự.",
        "password_length": "Mật khẩu phải có ít nhất 8 ký tự.",
        "password_mismatch": "Mật khẩu xác nhận không khớp.",
        "username_exists": "Tên đăng nhập đã tồn tại.",
        "register_success": "Đăng ký thành công. Hãy đăng nhập.",
        "login_failed": "Tên đăng nhập hoặc mật khẩu không đúng.",
        "login_success": "Đăng nhập thành công.",
        "logout_success": "Bạn đã đăng xuất thành công.",
        "session_expired": "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
        "login_required": "Vui lòng đăng nhập để tiếp tục.",
    },
    "en": {
        "username_length": "Username must contain 3 to 80 characters.",
        "password_length": "Password must contain at least 8 characters.",
        "password_mismatch": "Passwords do not match.",
        "username_exists": "Username already exists.",
        "register_success": "Registration successful. Please log in.",
        "login_failed": "Invalid username or password.",
        "login_success": "Logged in successfully.",
        "logout_success": "You have logged out successfully.",
        "session_expired": "Your session has expired. Please log in again.",
        "login_required": "Please log in to continue.",
    },
}


def get_auth_language():
    """Return the currently selected interface language."""

    language = session.get("language", "vi")

    if language not in AUTH_MESSAGES:
        return "vi"

    return language


def auth_message(key):
    """Translate an authentication message."""

    language = get_auth_language()
    return AUTH_MESSAGES[language][key]


def clear_analysis_session():
    """Clear temporary analysis data without deleting history."""

    session.pop("health_input", None)
    session.pop("analysis_result", None)
    session.pop("analysis_id", None)


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    """Create a new user account."""

    if current_user.is_authenticated:
        return redirect(url_for("health_form"))

    language = get_auth_language()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password", ""
        )

        if not 3 <= len(username) <= 80:
            flash(auth_message("username_length"), "error")

        elif len(password) < 8:
            flash(auth_message("password_length"), "error")

        elif password != confirm_password:
            flash(auth_message("password_mismatch"), "error")

        elif User.query.filter_by(username=username).first():
            flash(auth_message("username_exists"), "error")

        else:
            new_user = User(username=username)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            flash(
                auth_message("register_success"),
                "success",
            )

            return redirect(url_for("auth.login"))

    return render_template(
        "register.html",
        language=language,
    )


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate a user and create a valid server session."""

    if current_user.is_authenticated:
        return redirect(url_for("health_form"))

    language = get_auth_language()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(
            username=username
        ).first()

        if user is None or not user.check_password(password):
            flash(auth_message("login_failed"), "error")

        else:
            # Clear any previous session before authentication.
            session.clear()
            session["language"] = language

            login_user(user, remember=False)

            # This value is configured in app.py at startup.
            session["server_session_id"] = (
                auth_blueprint.server_session_id
            )

            flash(
                auth_message("login_success"),
                "success",
            )

            return redirect(url_for("health_form"))

    return render_template(
        "login.html",
        language=language,
    )


@auth_blueprint.route("/logout", methods=["POST"])
@login_required
def logout():
    """Sign out and invalidate the complete user session."""

    language = get_auth_language()

    logout_user()
    session.clear()

    # Preserve only the interface language.
    session["language"] = language

    flash(
        AUTH_MESSAGES[language]["logout_success"],
        "success",
    )

    return redirect(url_for("auth.login"))
