from datetime import date

from fastapi import APIRouter, Response, status
from sqlalchemy import select

from app.db import SessionDep
from app.models import Book, Idea, JournalEntry, MoodLog
from app.routers.common import get_or_404
from app.schemas.mental import (
    BookIn,
    BookOut,
    BookUpdate,
    IdeaIn,
    IdeaOut,
    JournalEntryIn,
    JournalEntryOut,
    MoodLogIn,
    MoodLogOut,
)

router = APIRouter(tags=["mental"])


# ─── Libros ─────────────────────────────────────────────────
@router.get("/books", response_model=list[BookOut])
def list_books(session: SessionDep) -> list[Book]:
    return list(session.scalars(select(Book).order_by(Book.created_at.desc())))


@router.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookIn, session: SessionDep) -> Book:
    book = Book(**payload.model_dump())
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@router.patch("/books/{book_id}", response_model=BookOut)
def update_book(book_id: str, payload: BookUpdate, session: SessionDep) -> Book:
    book = get_or_404(session, Book, book_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    session.commit()
    return book


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: str, session: SessionDep) -> Response:
    session.delete(get_or_404(session, Book, book_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─── Mood ───────────────────────────────────────────────────
@router.get("/mood-logs", response_model=list[MoodLogOut])
def list_mood_logs(session: SessionDep, start: date | None = None) -> list[MoodLog]:
    query = select(MoodLog).order_by(MoodLog.date)
    if start is not None:
        query = query.where(MoodLog.date >= start)
    return list(session.scalars(query))


@router.put("/mood-logs/{day}", response_model=MoodLogOut)
def upsert_mood_log(day: date, payload: MoodLogIn, session: SessionDep) -> MoodLog:
    log = session.scalar(select(MoodLog).where(MoodLog.date == day))
    if log is None:
        log = MoodLog(date=day)
        session.add(log)
    for field, value in payload.model_dump().items():
        setattr(log, field, value)
    session.commit()
    session.refresh(log)
    return log


# ─── Diario ─────────────────────────────────────────────────
@router.get("/journal-entries", response_model=list[JournalEntryOut])
def list_journal_entries(session: SessionDep) -> list[JournalEntry]:
    return list(session.scalars(select(JournalEntry).order_by(JournalEntry.created_at.desc())))


@router.post(
    "/journal-entries", response_model=JournalEntryOut, status_code=status.HTTP_201_CREATED
)
def create_journal_entry(payload: JournalEntryIn, session: SessionDep) -> JournalEntry:
    entry = JournalEntry(**payload.model_dump())
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.delete("/journal-entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_entry(entry_id: str, session: SessionDep) -> Response:
    session.delete(get_or_404(session, JournalEntry, entry_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─── Ideas ──────────────────────────────────────────────────
@router.get("/ideas", response_model=list[IdeaOut])
def list_ideas(session: SessionDep) -> list[Idea]:
    return list(session.scalars(select(Idea).order_by(Idea.created_at.desc())))


@router.post("/ideas", response_model=IdeaOut, status_code=status.HTTP_201_CREATED)
def create_idea(payload: IdeaIn, session: SessionDep) -> Idea:
    idea = Idea(**payload.model_dump())
    session.add(idea)
    session.commit()
    session.refresh(idea)
    return idea


@router.delete("/ideas/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_idea(idea_id: str, session: SessionDep) -> Response:
    session.delete(get_or_404(session, Idea, idea_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
