from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.mental.mental_model import Book, Idea, JournalEntry, MoodLog


def list_books(session: Session) -> list[Book]:
    return list(session.scalars(select(Book).order_by(Book.created_at.desc())))


def list_mood_logs(session: Session, start: date | None) -> list[MoodLog]:
    query = select(MoodLog).order_by(MoodLog.date)
    if start is not None:
        query = query.where(MoodLog.date >= start)
    return list(session.scalars(query))


def avg_mood(session: Session, start: date, end: date) -> float | None:
    avg = session.scalar(
        select(func.avg(MoodLog.mood_score)).where(MoodLog.date.between(start, end))
    )
    return float(avg) if avg is not None else None


def mood_log_of(session: Session, day: date) -> MoodLog | None:
    return session.scalar(select(MoodLog).where(MoodLog.date == day))


def list_journal_entries(session: Session) -> list[JournalEntry]:
    return list(session.scalars(select(JournalEntry).order_by(JournalEntry.created_at.desc())))


def list_ideas(session: Session, tag: str | None) -> list[Idea]:
    query = select(Idea).order_by(Idea.created_at.desc())
    if tag is not None:
        query = query.where(Idea.tag == tag)
    return list(session.scalars(query))


def tag_counts(session: Session) -> list[tuple[str, int]]:
    """Etiquetas en uso, de la más usada a la menos."""
    count = func.count(Idea.id)
    query = select(Idea.tag, count).group_by(Idea.tag).order_by(count.desc(), Idea.tag)
    return [(tag, n) for tag, n in session.execute(query)]
