"""Auth: login, sesión (JWT) y el único usuario de la app. Es lo único que ven los otros módulos."""

from app.modules.auth.auth_controller import router
from app.modules.auth.auth_dependency import CurrentUser, get_current_user
from app.modules.auth.auth_model import User

__all__ = ["CurrentUser", "User", "get_current_user", "router"]
