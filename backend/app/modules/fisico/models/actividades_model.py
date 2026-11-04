from typing import Any

from sqlalchemy import CHAR, JSON, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import COLOR, EMOJI, NAME, Base, CreatedAt, UUIDPk


class Activity(UUIDPk, CreatedAt, Base):
    """Algo que entrenás (gym, correr, estiramientos…). La definís vos desde la app."""

    __tablename__ = "activities"

    name: Mapped[str] = mapped_column(String(NAME))
    emoji: Mapped[str | None] = mapped_column(String(EMOJI))
    color: Mapped[str | None] = mapped_column(String(COLOR), default="#0A84FF")
    active: Mapped[bool] = mapped_column(Boolean, default=True)  # pausada = False
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    # Qué se anota en cada sesión: [{id, name, type, unit, options, archived}]
    fields: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    # Con hábito vinculado, la asistencia se marca en el hábito (sync con el dashboard)
    habit_id: Mapped[str | None] = mapped_column(
        CHAR(36), ForeignKey("habits.id", ondelete="SET NULL")
    )
