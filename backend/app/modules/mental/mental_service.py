from datetime import date

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
    MoodLogIn,
)


# ─── Libros ─────────────────────────────────────────────────
def list_books(session: Session) -> list[Book]:
    return repository.list_books(session)


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
def list_ideas(session: Session) -> list[Idea]:
    return repository.list_ideas(session)


def create_idea(session: Session, payload: IdeaIn) -> Idea:
    return base_repository.save(session, Idea(**payload.model_dump()))


def delete_idea(session: Session, idea_id: str) -> None:
    base_repository.delete(session, get_or_404(session, Idea, idea_id))
