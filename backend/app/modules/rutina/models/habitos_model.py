from datetime import date, time

from sqlalchemy import (
    CHAR,
    JSON,
    Boolean,
    Date,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import COLOR, EMOJI, NAME, Base, CreatedAt, UUIDPk


class Habit(UUIDPk, CreatedAt, Base):
    __tablename__ = "habits"

    name: Mapped[str] = mapped_column(String(NAME))
    color: Mapped[str | None] = mapped_column(String(COLOR), default="#30D158")
    emoji: Mapped[str | None] = mapped_column(String(EMOJI))
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    start_time: Mapped[time | None] = mapped_column(Time)
    duration_min: Mapped[int | None] = mapped_column(Integer, default=30)
    # null = todos los días; lista de 0..6 con 0 = lunes
    days_of_week: Mapped[list[int] | None] = mapped_column(JSON)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class HabitLog(UUIDPk, CreatedAt, Base):
    __tablename__ = "habit_logs"
    __table_args__ = (UniqueConstraint("habit_id", "date"),)

    habit_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("habits.id", ondelete="CASCADE"))
    date: Mapped[date] = mapped_column(Date, index=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
