# Backend — LifeOS API

FastAPI + SQLAlchemy 2 + MySQL. Dependencias gestionadas con [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`).

## Setup

```bash
cd backend
uv sync                 # crea .venv e instala todo (prod + dev)
cp .env.example .env    # completar DATABASE_URL
```

## Ejecutar

```bash
uv run uvicorn app.main:app --reload    # http://localhost:8000/health · docs en /docs
```

Para usar el entorno sin `uv run`: `source .venv/bin/activate`.

## Calidad

```bash
uv run pytest           # tests + cobertura
uv run ruff check .     # lint
uv run ruff format .    # formateo
uv run mypy app tests   # tipos
```

## Autenticación

Toda la API bajo `/api` exige `Authorization: Bearer <token>`, salvo `POST /api/auth/login`. Hay un único usuario y no existe registro público: se crea desde la terminal.

```bash
uv run python -m app.cli create-user     # pide usuario y contraseña (mín. 12 caracteres)
uv run python -m app.cli set-password    # cambia la contraseña y cierra todas las sesiones
```

- Contraseña guardada con Argon2id; nunca en texto plano.
- Tokens JWT firmados con `JWT_SECRET`, válidos `ACCESS_TOKEN_DAYS` días (30 por defecto).
- 5 logins fallidos por IP bloquean el login 15 minutos.
- En producción (`ENVIRONMENT=production`) no se publican `/docs`, `/redoc` ni `/openapi.json`.

## Migraciones

```bash
uv run alembic revision --autogenerate -m "mensaje"
uv run alembic upgrade head
```

La URL de la base se toma de `DATABASE_URL` en `.env`, no de `alembic.ini`.

## Deploy (Railway)

El servicio se construye con el `Dockerfile` (config en `railway.json`). Al arrancar aplica `alembic upgrade head` y levanta Uvicorn en `$PORT`. Healthcheck: `/health`.

Variables del servicio:

| Variable | Valor |
|---|---|
| `DATABASE_URL` | `${{MySQL.MYSQL_URL}}` (referencia al servicio MySQL; `mysql://` se convierte solo a `mysql+pymysql://`) |
| `CORS_ORIGINS` | `["https://<tu-app>.vercel.app"]` |
| `ENVIRONMENT` | `production` |
| `JWT_SECRET` | clave aleatoria propia (≥ 32 caracteres), distinta de la local |

Crear el usuario en producción, una vez desplegado: `railway ssh` en el servicio del backend y ahí `python -m app.cli create-user`.

La base MySQL de Railway debe quedar solo en la red privada: no actives su *TCP Proxy* público.
