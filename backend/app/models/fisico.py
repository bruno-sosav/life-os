from datetime import date
from decimal import Decimal

from sqlalchemy import (
    CHAR,
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

from app.core.base_model import NAME, Base, CreatedAt, UUIDPk


class GymSession(UUIDPk, CreatedAt, Base):
    __tablename__ = "gym_sessions"

    date: Mapped[date] = mapped_column(Date, index=True)
    attended: Mapped[bool] = mapped_column(Boolean, default=True)
    routine_name: Mapped[str | None] = mapped_column(String(NAME))
    notes: Mapped[str | None] = mapped_column(Text)

    exercises: Mapped[list["GymExercise"]] = relationship(
        cascade="all, delete-orphan", passive_deletes=True
    )


class GymExercise(UUIDPk, Base):
    __tablename__ = "gym_exercises"

    session_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("gym_sessions.id", ondelete="CASCADE"), index=True
    )
    exercise_name: Mapped[str] = mapped_column(String(NAME))
    sets: Mapped[int | None] = mapped_column(Integer)
    reps: Mapped[int | None] = mapped_column(Integer)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    notes: Mapped[str | None] = mapped_column(Text)


class MmaSession(UUIDPk, CreatedAt, Base):
    __tablename__ = "mma_sessions"

    date: Mapped[date] = mapped_column(Date, index=True)
    attended: Mapped[bool] = mapped_column(Boolean, default=True)
    session_type: Mapped[str | None] = mapped_column(String(NAME))
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
