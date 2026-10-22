from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.mental.mental_model import Book, Idea, JournalEntry, MoodLog


def list_books(session: Session) -> list[Book]:
    return list(session.scalars(select(Book).order_by(Book.created_at.desc())))


def list_mood_logs(session: Session, start: date | None) -> list[MoodLog]:
    query = select(MoodLog).order_by(MoodLog.date)
    if start is not None:
        query = query.where(MoodLog.date >= start)
    return list(session.scalars(query))


def mood_log_of(session: Session, day: date) -> MoodLog | None:
    return session.scalar(select(MoodLog).where(MoodLog.date == day))


def list_journal_entries(session: Session) -> list[JournalEntry]:
    return list(session.scalars(select(JournalEntry).order_by(JournalEntry.created_at.desc())))


def list_ideas(session: Session) -> list[Idea]:
    return list(session.scalars(select(Idea).order_by(Idea.created_at.desc())))
