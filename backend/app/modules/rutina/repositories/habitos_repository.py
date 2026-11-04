from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.rutina.models.habitos_model import Habit, HabitLog


def list_habits(session: Session, active: bool | None) -> list[Habit]:
    """Primero los que tienen horario (en orden), después los que no."""
    query = select(Habit).order_by(
        Habit.start_time.is_(None), Habit.start_time, Habit.sort_order, Habit.created_at
    )
    if active is not None:
        query = query.where(Habit.active == active)
    return list(session.scalars(query))


def completed_habit_logs(session: Session, start: date, end: date) -> list[tuple[str, date]]:
    """(habit_id, fecha) de cada hábito activo cumplido en el rango."""
    query = (
        select(HabitLog.habit_id, HabitLog.date)
        .join(Habit)
        .where(Habit.active.is_(True), HabitLog.completed.is_(True))
        .where(HabitLog.date.between(start, end))
    )
    return [(habit_id, day) for habit_id, day in session.execute(query)]


def habit_log_of(session: Session, habit_id: str, day: date) -> HabitLog | None:
    return session.scalar(
        select(HabitLog).where(HabitLog.habit_id == habit_id, HabitLog.date == day)
    )
