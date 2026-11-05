from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.seguridad.contrasena_util import verify_password
from app.core.seguridad.limite_intentos_util import login_throttle
from app.core.seguridad.token_util import UNAUTHORIZED, create_token, read_token
from app.modules.auth.models.usuarios_model import User
from app.modules.auth.repositories import usuarios_repository
from app.modules.auth.services import usuarios_service


def authenticate(session: Session, username: str, password: str) -> User | None:
    user = usuarios_repository.user_by_username(
        session, usuarios_service.normalize_username(username)
    )
    # verify_password corre aunque el usuario no exista: el tiempo de respuesta no lo delata
    if not verify_password(password, user.password_hash if user else None):
        return None
    return user


def login(session: Session, username: str, password: str, client_ip: str) -> tuple[str, datetime]:
    login_throttle.check(client_ip)
    user = authenticate(session, username, password)
    if user is None:
        login_throttle.fail(client_ip)
        # Mismo mensaje para usuario inexistente y contraseña incorrecta
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario o contraseña incorrectos")
    login_throttle.reset(client_ip)
    return create_token(user.id, user.token_version)


def user_from_token(session: Session, token: str) -> User:
    user_id, version = read_token(token)
    user = usuarios_repository.user_by_id(session, user_id)
    if user is None or user.token_version != version:
        raise UNAUTHORIZED
    return user
