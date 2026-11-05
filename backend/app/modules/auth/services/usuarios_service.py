from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.seguridad.contrasena_util import hash_password
from app.modules.auth.models.usuarios_model import User
from app.modules.auth.repositories import usuarios_repository

MIN_PASSWORD_LENGTH = 12

MAX_USERNAME_LENGTH = 50


def normalize_username(username: str) -> str:
    return username.strip().lower()


def check_new_username(session: Session, username: str) -> str:
    username = normalize_username(username)
    if not 1 <= len(username) <= MAX_USERNAME_LENGTH:
        raise ValueError(f"Usuario inválido (1 a {MAX_USERNAME_LENGTH} caracteres).")
    if usuarios_repository.user_by_username(session, username) is not None:
        raise ValueError(
            f"El usuario '{username}' ya existe. Usá set-password para cambiarle la clave."
        )
    return username


def existing_user(session: Session, username: str) -> User:
    user = usuarios_repository.user_by_username(session, normalize_username(username))
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
