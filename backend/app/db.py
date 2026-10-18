from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

# create_engine no abre conexiones: la primera se abre al usar una sesión.
# La sesión de MySQL trabaja en UTC para que CURRENT_TIMESTAMP sea consistente.
engine = create_engine(
    get_settings().database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"init_command": "SET time_zone = '+00:00'"},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# Nombres de constraints estables para que Alembic genere migraciones predecibles.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
