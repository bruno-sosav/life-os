from datetime import date

from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.mental import mental_service as service
from app.modules.mental.mental_model import Book, Idea, JournalEntry, MoodLog
from app.modules.mental.mental_schema import (
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
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/books", response_model=list[BookOut])
def list_books(session: SessionDep) -> list[Book]:
    return service.list_books(session)


@router.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookIn, session: SessionDep) -> Book:
    return service.create_book(session, payload)


@router.patch("/books/{book_id}", response_model=BookOut)
def update_book(book_id: str, payload: BookUpdate, session: SessionDep) -> Book:
    return service.update_book(session, book_id, payload)


@router.delete("/books/{book_id}", status_code=NO_CONTENT)
def delete_book(book_id: str, session: SessionDep) -> Response:
    service.delete_book(session, book_id)
    return Response(status_code=NO_CONTENT)


@router.get("/mood-logs", response_model=list[MoodLogOut])
def list_mood_logs(session: SessionDep, start: date | None = None) -> list[MoodLog]:
    return service.list_mood_logs(session, start)


@router.put("/mood-logs/{day}", response_model=MoodLogOut)
def upsert_mood_log(day: date, payload: MoodLogIn, session: SessionDep) -> MoodLog:
    return service.upsert_mood_log(session, day, payload)


@router.get("/journal-entries", response_model=list[JournalEntryOut])
def list_journal_entries(session: SessionDep) -> list[JournalEntry]:
    return service.list_journal_entries(session)


@router.post(
    "/journal-entries", response_model=JournalEntryOut, status_code=status.HTTP_201_CREATED
)
def create_journal_entry(payload: JournalEntryIn, session: SessionDep) -> JournalEntry:
    return service.create_journal_entry(session, payload)


@router.delete("/journal-entries/{entry_id}", status_code=NO_CONTENT)
def delete_journal_entry(entry_id: str, session: SessionDep) -> Response:
    service.delete_journal_entry(session, entry_id)
    return Response(status_code=NO_CONTENT)


@router.get("/ideas", response_model=list[IdeaOut])
def list_ideas(session: SessionDep) -> list[Idea]:
    return service.list_ideas(session)


@router.post("/ideas", response_model=IdeaOut, status_code=status.HTTP_201_CREATED)
def create_idea(payload: IdeaIn, session: SessionDep) -> Idea:
    return service.create_idea(session, payload)


@router.delete("/ideas/{idea_id}", status_code=NO_CONTENT)
def delete_idea(idea_id: str, session: SessionDep) -> Response:
    service.delete_idea(session, idea_id)
    return Response(status_code=NO_CONTENT)
