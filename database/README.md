# Database

Scripts para la base MySQL local. El schema lo definen los modelos y las migraciones de Alembic en `backend/`.

- `setup_mysql.sh`: crea la base y el usuario `lifeos`, escribe `backend/.env` y prueba la conexión. Pide las contraseñas por teclado.

  ```bash
  ./database/setup_mysql.sh
  cd backend && uv run alembic upgrade head
  ```
