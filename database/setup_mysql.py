#!/usr/bin/env python3
"""Crea la base `lifeos` y el usuario `lifeos` en el MySQL local, escribe backend/.env
y prueba la conexión desde la app. Las contraseñas se piden por teclado y no quedan
en el historial ni en la lista de procesos.

    python3 database/setup_mysql.py
"""

import getpass
import os
import secrets
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

MYSQL = os.environ.get("MYSQL", "/usr/local/mysql/bin/mysql")
DB_NAME = "lifeos"
DB_USER = "lifeos"
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
ENV_FILE = BACKEND_DIR / ".env"


def sql_literal(value: str) -> str:
    """Escapa \\ y ' para usar el valor dentro de un literal SQL."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def main() -> None:
    if ENV_FILE.exists() and input(".env ya existe en backend/. ¿Sobrescribirlo? [s/N] ").lower() != "s":
        sys.exit("Cancelado.")

    root_pass = getpass.getpass("Contraseña de root de MySQL: ")
    app_pass = getpass.getpass(f"Nueva contraseña para el usuario '{DB_USER}': ")
    if not app_pass:
        sys.exit("La contraseña no puede estar vacía.")
    if getpass.getpass("Repetila: ") != app_pass:
        sys.exit("Las contraseñas no coinciden.")

    pw = sql_literal(app_pass)
    sql = f"""
CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER IF NOT EXISTS '{DB_USER}'@'localhost' IDENTIFIED BY '{pw}';
ALTER USER '{DB_USER}'@'localhost' IDENTIFIED BY '{pw}';
GRANT ALL PRIVILEGES ON `{DB_NAME}`.* TO '{DB_USER}'@'localhost';
FLUSH PRIVILEGES;
"""
    # El SQL va por stdin y la contraseña de root por variable de entorno, no como argumentos
    env = {**os.environ, "MYSQL_PWD": root_pass}
    if subprocess.run([MYSQL, "-u", "root"], input=sql, text=True, env=env).returncode:
        sys.exit("MySQL rechazó el comando (¿contraseña de root correcta?).")
    print(f"✔ Base '{DB_NAME}' y usuario '{DB_USER}' listos.")

    # quote: la contraseña puede tener @ : / # que romperían la URL
    ENV_FILE.write_text(
        'APP_NAME="LifeOS API"\n'
        "ENVIRONMENT=development\n"
        "DEBUG=false\n"
        f"DATABASE_URL=mysql+pymysql://{DB_USER}:{quote(app_pass, safe='')}"
        f"@localhost:3306/{DB_NAME}?charset=utf8mb4\n"
        f"JWT_SECRET={secrets.token_urlsafe(64)}\n"
    )
    ENV_FILE.chmod(0o600)
    print("✔ backend/.env escrito.")

    check = (
        "from sqlalchemy import text\n"
        "from app.core.database.conexion_database import engine\n"
        "with engine.connect() as c:\n"
        "    print('✔ Conexión OK — MySQL', c.execute(text('SELECT VERSION()')).scalar())\n"
    )
    sys.exit(subprocess.run(["uv", "run", "python", "-c", check], cwd=BACKEND_DIR).returncode)


if __name__ == "__main__":
    main()
