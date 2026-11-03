from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    CHAR,
    JSON,
    Boolean,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base_model import NAME, Base, CreatedAt, UUIDPk


class ActivitySession(UUIDPk, CreatedAt, Base):
    __tablename__ = "activity_sessions"

    activity_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("activities.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[date] = mapped_column(Date, index=True)
    attended: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    # Valores de los campos de la actividad: {field_id: valor}
    values: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    exercises: Mapped[list["SessionExercise"]] = relationship(
        cascade="all, delete-orphan", passive_deletes=True
    )


class SessionExercise(UUIDPk, Base):
    """Fila de un campo de tipo "ejercicios" (gym, calistenia…)."""

    __tablename__ = "session_exercises"

    session_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("activity_sessions.id", ondelete="CASCADE"), index=True
    )
    exercise_name: Mapped[str] = mapped_column(String(NAME))
    sets: Mapped[int | None] = mapped_column(Integer)
    reps: Mapped[int | None] = mapped_column(Integer)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    notes: Mapped[str | None] = mapped_column(Text)
