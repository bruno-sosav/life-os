#!/usr/bin/env bash
# Crea la base `lifeos` y el usuario `lifeos` en el MySQL local, escribe backend/.env
# y prueba la conexión desde SQLAlchemy. Las contraseñas se piden por teclado y no
# quedan en el historial ni en la lista de procesos.
set -euo pipefail

MYSQL="${MYSQL:-/usr/local/mysql/bin/mysql}"
DB_NAME="lifeos"
DB_USER="lifeos"
BACKEND_DIR="$(cd "$(dirname "$0")/../backend" && pwd)"
ENV_FILE="$BACKEND_DIR/.env"

if [[ -f "$ENV_FILE" ]]; then
  read -r -p ".env ya existe en backend/. ¿Sobrescribirlo? [s/N] " answer
  [[ "$answer" =~ ^[sS]$ ]] || { echo "Cancelado."; exit 1; }
fi

read -r -s -p "Contraseña de root de MySQL: " ROOT_PASS; echo
read -r -s -p "Nueva contraseña para el usuario '$DB_USER': " APP_PASS; echo
read -r -s -p "Repetila: " APP_PASS2; echo
[[ "$APP_PASS" == "$APP_PASS2" ]] || { echo "Las contraseñas no coinciden."; exit 1; }
[[ -n "$APP_PASS" ]] || { echo "La contraseña no puede estar vacía."; exit 1; }

# Escapar \ y ' para usarla dentro de un literal SQL
SQL_PASS="${APP_PASS//\\/\\\\}"
SQL_PASS="${SQL_PASS//\'/\\\'}"

# La contraseña de root va por variable de entorno, no como argumento
MYSQL_PWD="$ROOT_PASS" "$MYSQL" -u root <<SQL
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$SQL_PASS';
ALTER USER '$DB_USER'@'localhost' IDENTIFIED BY '$SQL_PASS';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
SQL
echo "✔ Base '$DB_NAME' y usuario '$DB_USER' listos."

# Codificar la contraseña para la URL (caracteres como @ : / #)
URL_PASS="$(APP_PASS="$APP_PASS" python3 -c 'import os, urllib.parse; print(urllib.parse.quote(os.environ["APP_PASS"], safe=""))')"

cat > "$ENV_FILE" <<ENV
APP_NAME="LifeOS API"
ENVIRONMENT=development
DEBUG=false
DATABASE_URL=mysql+pymysql://$DB_USER:$URL_PASS@localhost:3306/$DB_NAME?charset=utf8mb4
ENV
chmod 600 "$ENV_FILE"
echo "✔ backend/.env escrito."

cd "$BACKEND_DIR"
uv run python -c "
from sqlalchemy import text
from app.db import engine
with engine.connect() as c:
    print('✔ Conexión OK — MySQL', c.execute(text('SELECT VERSION()')).scalar())
"
