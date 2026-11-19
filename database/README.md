# Database

Scripts para la base MySQL local. El schema lo definen los modelos y las migraciones de Alembic en `backend/`.

- `setup_mysql.py`: crea la base y el usuario `lifeos`, escribe `backend/.env` (con una `JWT_SECRET` nueva) y prueba la conexión. Pide las contraseñas por teclado. Si el cliente `mysql` no está en `/usr/local/mysql/bin/mysql`, pasá la ruta con `MYSQL=/ruta/a/mysql`.

  ```bash
  python3 database/setup_mysql.py
  cd backend && uv run alembic upgrade head
  ```
