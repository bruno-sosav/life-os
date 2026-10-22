from datetime import datetime
from uuid import uuid4

from sqlalchemy import CHAR, DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Largos de columnas cortas reutilizados en todos los modelos
NAME = 255
COLOR = 20  # '#30D158'
EMOJI = 32  # algunos emojis son varios code points
STATUS = 30


def new_uuid() -> str:
    return str(uuid4())


class UUIDPk:
    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=new_uuid, sort_order=-1)


class CreatedAt:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), sort_order=1)
