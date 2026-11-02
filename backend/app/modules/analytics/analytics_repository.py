"""Analytics no tiene tablas propias. Lo de rutina lo pide a rutina; acá lee el resto."""

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.finanzas import FinanceExpense, FinanceIncome
from app.modules.fisico import WeightLog
from app.modules.mental import Book, JournalEntry, MoodLog


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
