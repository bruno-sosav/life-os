import os

# Antes de importar la app: la configuración exige JWT_SECRET.
os.environ.setdefault("JWT_SECRET", "test-secret-" + "x" * 40)

from collections.abc import Iterator  # noqa: E402
from typing import Any  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app import models  # noqa: E402, F401  registra las tablas
from app.core.database.base_model import Base  # noqa: E402
from app.core.database.conexion_database import get_session  # noqa: E402
from app.core.seguridad.contrasena_util import hash_password  # noqa: E402
from app.core.seguridad.limite_intentos_util import login_throttle  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402

USERNAME = "bruno"
PASSWORD = "una-clave-de-prueba-larga"


@pytest.fixture
def db() -> Iterator[sessionmaker[Session]]:
    # SQLite en memoria: rápido y sin setup. La base real es MySQL; lo específico
    # de MySQL se verifica con las migraciones de Alembic.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    @event.listens_for(engine, "connect")
    def _enable_fks(dbapi_conn: Any, _: Any) -> None:
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with factory() as session:
        session.add(User(username=USERNAME, password_hash=hash_password(PASSWORD)))
        session.commit()

    def _get_session() -> Iterator[Session]:
        with factory() as session:
            yield session

    app.dependency_overrides[get_session] = _get_session
    login_throttle._failures.clear()
    yield factory
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def anon_client(db: sessionmaker[Session]) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def client(anon_client: TestClient) -> TestClient:
    """Cliente con sesión iniciada."""
    response = anon_client.post(
        "/api/auth/login", json={"username": USERNAME, "password": PASSWORD}
    )
    anon_client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
    return anon_client
