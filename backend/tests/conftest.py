from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  registra las tablas
from app.db import Base, get_session
from app.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    # SQLite en memoria: rápido y sin setup. La base real es MySQL; lo específico
    # de MySQL se verifica con las migraciones de Alembic.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    @event.listens_for(engine, "connect")
    def _enable_fks(dbapi_conn: Any, _: Any) -> None:
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def _get_session() -> Iterator[Session]:
        with testing_session() as session:
            yield session

    app.dependency_overrides[get_session] = _get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()
