"""Gestión del usuario desde la terminal (no hay registro público por la API).

uv run python -m app.cli create-user     # crea el usuario
uv run python -m app.cli set-password    # cambia la contraseña y cierra todas las sesiones
"""

import argparse
import getpass
import sys

from app.core.database.conexion_database import SessionLocal
from app.modules.auth import auth_service as service


def ask_password() -> str:
    password = getpass.getpass("Contraseña: ")
    service.check_password(password)
    if getpass.getpass("Repetila: ") != password:
        raise ValueError("Las contraseñas no coinciden.")
    return password


def create_user() -> None:
    with SessionLocal() as session:
        username = service.check_new_username(session, input("Usuario: "))
        service.create_user(session, username, ask_password())
    print(f"✔ Usuario '{username}' creado.")


def set_password() -> None:
    with SessionLocal() as session:
        user = service.existing_user(session, input("Usuario: "))
        service.set_password(session, user.username, ask_password())
    print(f"✔ Contraseña de '{user.username}' actualizada. Las sesiones abiertas se cerraron.")


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    parser.add_argument("command", choices=["create-user", "set-password"])
    args = parser.parse_args()
    try:
        {"create-user": create_user, "set-password": set_password}[args.command]()
    except ValueError as error:
        sys.exit(str(error))


if __name__ == "__main__":
    main()
