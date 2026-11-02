from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    CHAR,
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


class WeightLog(UUIDPk, CreatedAt, Base):
    __tablename__ = "weight_logs"

    date: Mapped[date] = mapped_column(Date, unique=True)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    notes: Mapped[str | None] = mapped_column(Text)


class NutritionLog(UUIDPk, CreatedAt, Base):
    __tablename__ = "nutrition_logs"
    __table_args__ = (CheckConstraint("quality_score BETWEEN 1 AND 5", name="quality_score"),)

    date: Mapped[date] = mapped_column(Date, unique=True)
    quality_score: Mapped[int | None] = mapped_column(Integer)
    meals_count: Mapped[int | None] = mapped_column(Integer)
    water_liters: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    notes: Mapped[str | None] = mapped_column(Text)
