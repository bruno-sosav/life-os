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

## Migraciones

```bash
uv run alembic revision --autogenerate -m "mensaje"
uv run alembic upgrade head
```

La URL de la base se toma de `DATABASE_URL` en `.env`, no de `alembic.ini`.
