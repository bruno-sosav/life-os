"""Dashboard no tiene tablas propias: lee las de rutina, físico y mental (solo lectura)."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.fisico import GymSession, MmaSession
from app.modules.mental import MoodLog
from app.modules.rutina import Habit, HabitLog, RoutineBlock, RoutineCompletion, WeeklyReview


def active_habits(session: Session) -> list[Habit]:
    query = select(Habit).where(Habit.active.is_(True)).order_by(Habit.sort_order, Habit.created_at)
    return list(session.scalars(query))


def routine_blocks(session: Session) -> list[RoutineBlock]:
    return list(session.scalars(select(RoutineBlock).order_by(RoutineBlock.hour_start)))


def completed_habit_dates(session: Session, start: date, end: date) -> list[date]:
    """Una fecha por cada hábito activo cumplido en el rango."""
    query = (
        select(HabitLog.date)
        .join(Habit)
        .where(Habit.active.is_(True), HabitLog.completed.is_(True))
        .where(HabitLog.date.between(start, end))
    )
    return list(session.scalars(query))


def completed_block_dates(session: Session, start: date, end: date) -> list[date]:
    query = select(RoutineCompletion.date).where(RoutineCompletion.date.between(start, end))
    return list(session.scalars(query))


def done_block_ids(session: Session, day: date) -> set[str]:
    query = select(RoutineCompletion.block_id).where(RoutineCompletion.date == day)
    return set(session.scalars(query))


def done_habit_ids(session: Session, day: date) -> set[str]:
    query = select(HabitLog.habit_id).where(HabitLog.date == day, HabitLog.completed.is_(True))
    return set(session.scalars(query))


def attended_days(
    session: Session, model: type[GymSession | MmaSession], start: date, end: date
) -> int:
    query = (
        select(func.count(func.distinct(model.date)))
        .where(model.attended.is_(True))
        .where(model.date.between(start, end))
    )
    return session.scalar(query) or 0


def avg_mood(session: Session, start: date, end: date) -> float | None:
    avg = session.scalar(
        select(func.avg(MoodLog.mood_score)).where(MoodLog.date.between(start, end))
    )
    return float(avg) if avg is not None else None


def weekly_review_of(session: Session, week_start: date) -> WeeklyReview | None:
    return session.scalar(select(WeeklyReview).where(WeeklyReview.week_start == week_start))
