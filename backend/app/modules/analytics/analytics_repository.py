"""Analytics no tiene tablas propias: lee las de rutina, físico, mental y finanzas."""

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.finanzas import FinanceExpense, FinanceIncome
from app.modules.fisico import GymSession, MmaSession, WeightLog
from app.modules.mental import Book, JournalEntry, MoodLog
from app.modules.rutina import Habit, HabitLog, RoutineBlock, RoutineCompletion


def active_habits(session: Session) -> list[Habit]:
    return list(session.scalars(select(Habit).where(Habit.active.is_(True))))


def routine_blocks(session: Session) -> list[RoutineBlock]:
    return list(session.scalars(select(RoutineBlock)))


def habit_logs(session: Session, start: date, end: date) -> list[tuple[Any, ...]]:
    """(habit_id, date) de los hábitos activos cumplidos en el rango."""
    query = (
        select(HabitLog.habit_id, HabitLog.date)
        .join(Habit)
        .where(Habit.active.is_(True), HabitLog.completed.is_(True))
        .where(HabitLog.date.between(start, end))
    )
    return [tuple(row) for row in session.execute(query)]


def block_completions(session: Session, start: date, end: date) -> list[tuple[Any, ...]]:
    query = select(RoutineCompletion.block_id, RoutineCompletion.date).where(
        RoutineCompletion.date.between(start, end)
    )
    return [tuple(row) for row in session.execute(query)]


def attended_dates(
    session: Session, model: type[GymSession | MmaSession], start: date
) -> list[date]:
    query = select(model.date).where(model.attended.is_(True), model.date >= start)
    return list(session.scalars(query))


def moods(session: Session, start: date, end: date) -> list[tuple[Any, ...]]:
    query = select(MoodLog.date, MoodLog.mood_score, MoodLog.sleep_hours).where(
        MoodLog.date.between(start, end)
    )
    return [tuple(row) for row in session.execute(query)]


def weights(session: Session) -> list[tuple[Any, ...]]:
    return [tuple(row) for row in session.execute(select(WeightLog.date, WeightLog.weight_kg))]


def journal_dates(session: Session, start: date) -> list[date]:
    return list(session.scalars(select(JournalEntry.date).where(JournalEntry.date >= start)))


def finished_book_dates(session: Session) -> list[date]:
    query = select(Book.finished_at).where(Book.status == "leido", Book.finished_at.is_not(None))
    return [d for d in session.scalars(query) if d is not None]


def income(session: Session, start: date) -> list[tuple[Any, ...]]:
    query = select(FinanceIncome.month, FinanceIncome.amount).where(FinanceIncome.month >= start)
    return [tuple(row) for row in session.execute(query)]


def expenses(session: Session, start: date) -> list[tuple[Any, ...]]:
    query = select(FinanceExpense.date, FinanceExpense.amount).where(FinanceExpense.date >= start)
    return [tuple(row) for row in session.execute(query)]
