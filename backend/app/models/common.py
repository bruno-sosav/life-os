from datetime import datetime
from uuid import uuid4

from sqlalchemy import CHAR, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

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
