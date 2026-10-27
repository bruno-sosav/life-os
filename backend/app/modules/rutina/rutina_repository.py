from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.rutina.rutina_model import (
    Habit,
    HabitLog,
    RoutineBlock,
    RoutineCompletion,
    WeeklyReview,
)


# ─── Hábitos ────────────────────────────────────────────────
def list_habits(session: Session, active: bool | None, linked_module: str | None) -> list[Habit]:
    """Primero los que tienen horario (en orden), después los que no."""
    query = select(Habit).order_by(
        Habit.start_time.is_(None), Habit.start_time, Habit.sort_order, Habit.created_at
    )
    if active is not None:
        query = query.where(Habit.active == active)
    if linked_module is not None:
        query = query.where(Habit.linked_module == linked_module)
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


# ─── Bloques de rutina ──────────────────────────────────────
def list_routine_blocks(session: Session) -> list[RoutineBlock]:
    return list(session.scalars(select(RoutineBlock).order_by(RoutineBlock.hour_start)))


def block_completions(session: Session, start: date, end: date) -> list[tuple[str, date]]:
    """(block_id, fecha) de cada bloque cumplido en el rango."""
    query = select(RoutineCompletion.block_id, RoutineCompletion.date).where(
        RoutineCompletion.date.between(start, end)
    )
    return [(block_id, day) for block_id, day in session.execute(query)]


def completion_of(session: Session, block_id: str, day: date) -> RoutineCompletion | None:
    return session.scalar(
        select(RoutineCompletion).where(
            RoutineCompletion.block_id == block_id, RoutineCompletion.date == day
        )
    )


# ─── Cierre semanal ─────────────────────────────────────────
def weekly_review_of(session: Session, week_start: date) -> WeeklyReview | None:
    return session.scalar(select(WeeklyReview).where(WeeklyReview.week_start == week_start))
