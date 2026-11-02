from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.modules.mental import mental_repository as repository
from app.modules.mental.mental_model import Book, Idea, JournalEntry, MoodLog
from app.modules.mental.mental_schema import (
    BookIn,
    BookUpdate,
    IdeaIn,
    JournalEntryIn,
    Library,
    MoodAverage,
    MoodLogIn,
    Shelves,
    TagCount,
)


# ─── Libros ─────────────────────────────────────────────────
def library(session: Session, today: date) -> Library:
    """Los libros agrupados por estante y cuántos se terminaron en el año de `today`."""
    books = repository.list_books(session)
    read = [b for b in books if b.status == "leido"]
    return Library(
        shelves=Shelves.model_validate(
            {status: [b for b in books if b.status == status] for status in Shelves.model_fields}
        ),
        year=today.year,
        read_this_year=sum(1 for b in read if b.finished_at and b.finished_at.year == today.year),
    )


def create_book(session: Session, payload: BookIn) -> Book:
    return base_repository.save(session, Book(**payload.model_dump()))


def update_book(session: Session, book_id: str, payload: BookUpdate) -> Book:
    book = get_or_404(session, Book, book_id)
    return base_repository.save(
        session, base_repository.apply(book, payload.model_dump(exclude_unset=True))
    )


def delete_book(session: Session, book_id: str) -> None:
    base_repository.delete(session, get_or_404(session, Book, book_id))


# ─── Mood (un registro por día) ─────────────────────────────
def list_mood_logs(session: Session, start: date | None) -> list[MoodLog]:
    return repository.list_mood_logs(session, start)


def avg_mood(session: Session, start: date, end: date) -> float | None:
    return repository.avg_mood(session, start, end)


def mood_average(session: Session, today: date) -> MoodAverage:
    avg = avg_mood(session, today - timedelta(days=6), today)
    return MoodAverage(avg_mood=round(avg, 1) if avg is not None else None)


def upsert_mood_log(session: Session, day: date, payload: MoodLogIn) -> MoodLog:
    log = repository.mood_log_of(session, day) or MoodLog(date=day)
    return base_repository.save(session, base_repository.apply(log, payload.model_dump()))


# ─── Diario ─────────────────────────────────────────────────
def list_journal_entries(session: Session) -> list[JournalEntry]:
    return repository.list_journal_entries(session)


def create_journal_entry(session: Session, payload: JournalEntryIn) -> JournalEntry:
    return base_repository.save(session, JournalEntry(**payload.model_dump()))


def delete_journal_entry(session: Session, entry_id: str) -> None:
    base_repository.delete(session, get_or_404(session, JournalEntry, entry_id))


# ─── Ideas ──────────────────────────────────────────────────
def list_ideas(session: Session, tag: str | None) -> list[Idea]:
    return repository.list_ideas(session, tag)


def list_tags(session: Session) -> list[TagCount]:
    return [TagCount(tag=tag, count=n) for tag, n in repository.tag_counts(session)]


def create_idea(session: Session, payload: IdeaIn) -> Idea:
    return base_repository.save(session, Idea(**payload.model_dump()))


def delete_idea(session: Session, idea_id: str) -> None:
    base_repository.delete(session, get_or_404(session, Idea, idea_id))
