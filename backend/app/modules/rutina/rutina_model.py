from datetime import date, datetime, time

from sqlalchemy import (
    CHAR,
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import COLOR, EMOJI, NAME, Base, CreatedAt, UUIDPk


class Habit(UUIDPk, CreatedAt, Base):
    __tablename__ = "habits"

    name: Mapped[str] = mapped_column(String(NAME))
    color: Mapped[str | None] = mapped_column(String(COLOR), default="#30D158")
    icon: Mapped[str | None] = mapped_column(String(EMOJI))
    emoji: Mapped[str | None] = mapped_column(String(EMOJI))
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    start_time: Mapped[time | None] = mapped_column(Time)
    duration_min: Mapped[int | None] = mapped_column(Integer, default=30)
    # null = todos los días; lista de 0..6 con 0 = lunes
    days_of_week: Mapped[list[int] | None] = mapped_column(JSON)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    # 'gym' | 'mma' | null: sincroniza el hábito con la pestaña Físico
    linked_module: Mapped[str | None] = mapped_column(String(20))


class HabitLog(UUIDPk, CreatedAt, Base):
    __tablename__ = "habit_logs"
    __table_args__ = (UniqueConstraint("habit_id", "date"),)

    habit_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("habits.id", ondelete="CASCADE"))
    date: Mapped[date] = mapped_column(Date, index=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    note: Mapped[str | None] = mapped_column(Text)


class RoutineBlock(UUIDPk, CreatedAt, Base):
    __tablename__ = "routine_blocks"

    # 0 = lunes … 6 = domingo; null si es un bloque de fecha puntual
    day_of_week: Mapped[int | None] = mapped_column(Integer)
    # lista de días cuando el bloque se repite en varios; null/[] = usa day_of_week
    days_of_week: Mapped[list[int] | None] = mapped_column(JSON)
    specific_date: Mapped[date | None] = mapped_column(Date)
    repeat_weekly: Mapped[bool] = mapped_column(Boolean, default=True)
    hour_start: Mapped[int] = mapped_column(Integer)
    hour_min: Mapped[int] = mapped_column(Integer, default=0)
    hour_end: Mapped[int] = mapped_column(Integer)
    activity: Mapped[str] = mapped_column(String(NAME))
    category: Mapped[str | None] = mapped_column(String(30))
    emoji: Mapped[str | None] = mapped_column(String(EMOJI))
    color: Mapped[str | None] = mapped_column(String(COLOR))


class RoutineCompletion(UUIDPk, Base):
    __tablename__ = "routine_completions"
    __table_args__ = (UniqueConstraint("block_id", "date"),)

    block_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("routine_blocks.id", ondelete="CASCADE")
    )
    date: Mapped[date] = mapped_column(Date, index=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class WeeklyReview(UUIDPk, CreatedAt, Base):
    __tablename__ = "weekly_reviews"

    week_start: Mapped[date] = mapped_column(Date, unique=True)  # lunes de esa semana
    went_well: Mapped[str | None] = mapped_column(Text)
    would_change: Mapped[str | None] = mapped_column(Text)
