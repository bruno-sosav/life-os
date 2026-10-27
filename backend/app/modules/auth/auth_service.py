from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.seguridad.contrasena_util import hash_password, verify_password
from app.core.seguridad.limite_intentos_util import login_throttle
from app.core.seguridad.token_util import UNAUTHORIZED, create_token, read_token
from app.modules.auth import auth_repository as repository
from app.modules.auth.auth_model import User

MIN_PASSWORD_LENGTH = 12
MAX_USERNAME_LENGTH = 50


def normalize_username(username: str) -> str:
    return username.strip().lower()


# ─── Login y sesión ─────────────────────────────────────────
def authenticate(session: Session, username: str, password: str) -> User | None:
    user = repository.user_by_username(session, normalize_username(username))
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
    user = repository.user_by_id(session, user_id)
    if user is None or user.token_version != version:
        raise UNAUTHORIZED
    return user


# ─── Gestión del usuario (solo desde la terminal, ver app/cli.py) ───
def check_new_username(session: Session, username: str) -> str:
    username = normalize_username(username)
    if not 1 <= len(username) <= MAX_USERNAME_LENGTH:
        raise ValueError(f"Usuario inválido (1 a {MAX_USERNAME_LENGTH} caracteres).")
    if repository.user_by_username(session, username) is not None:
        raise ValueError(
            f"El usuario '{username}' ya existe. Usá set-password para cambiarle la clave."
        )
    return username


def existing_user(session: Session, username: str) -> User:
    user = repository.user_by_username(session, normalize_username(username))
    if user is None:
        raise ValueError(f"El usuario '{normalize_username(username)}' no existe.")
    return user


def check_password(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres.")


def create_user(session: Session, username: str, password: str) -> User:
    username = check_new_username(session, username)
    check_password(password)
    return base_repository.save(
        session, User(username=username, password_hash=hash_password(password))
    )


def set_password(session: Session, username: str, password: str) -> User:
    """Cambia la contraseña y cierra todas las sesiones abiertas (sube token_version)."""
    user = existing_user(session, username)
    check_password(password)
    user.password_hash = hash_password(password)
    user.token_version += 1
    return base_repository.save(session, user)
