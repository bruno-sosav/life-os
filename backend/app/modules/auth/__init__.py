"""Auth: login, sesión (JWT) y el único usuario de la app. Es lo único que ven los otros módulos."""

from fastapi import APIRouter

from app.modules.auth.controllers import sesion_controller
from app.modules.auth.controllers.sesion_dependency import get_current_user
from app.modules.auth.models.usuarios_model import User

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(sesion_controller.router)

__all__ = ["User", "get_current_user", "router"]
