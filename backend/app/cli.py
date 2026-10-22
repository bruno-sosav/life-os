"""Gestión del usuario desde la terminal (no hay registro público por la API).

uv run python -m app.cli create-user     # crea el usuario
uv run python -m app.cli set-password    # cambia la contraseña y cierra todas las sesiones
"""

import argparse
import getpass
import sys

from sqlalchemy import select

from app.core.conexion_database import SessionLocal
from app.core.contrasena_util import hash_password
from app.models import User

MIN_PASSWORD_LENGTH = 12


def ask_password() -> str:
    password = getpass.getpass("Contraseña: ")
    if len(password) < MIN_PASSWORD_LENGTH:
        sys.exit(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres.")
    if getpass.getpass("Repetila: ") != password:
        sys.exit("Las contraseñas no coinciden.")
    return password


def create_user() -> None:
    username = input("Usuario: ").strip().lower()
    if not username or len(username) > 50:
        sys.exit("Usuario inválido (1 a 50 caracteres).")
    with SessionLocal() as session:
        if session.scalar(select(User).where(User.username == username)):
            sys.exit(
                f"El usuario '{username}' ya existe. Usá set-password para cambiarle la clave."
            )
        session.add(User(username=username, password_hash=hash_password(ask_password())))
        session.commit()
    print(f"✔ Usuario '{username}' creado.")


def set_password() -> None:
    username = input("Usuario: ").strip().lower()
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.username == username))
        if user is None:
            sys.exit(f"El usuario '{username}' no existe.")
        user.password_hash = hash_password(ask_password())
        user.token_version += 1
        session.commit()
    print(f"✔ Contraseña de '{username}' actualizada. Las sesiones abiertas se cerraron.")


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    parser.add_argument("command", choices=["create-user", "set-password"])
    args = parser.parse_args()
    {"create-user": create_user, "set-password": set_password}[args.command]()


if __name__ == "__main__":
    main()
