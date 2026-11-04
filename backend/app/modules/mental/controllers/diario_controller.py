from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.mental.models.diario_model import JournalEntry
from app.modules.mental.schemas.diario_schema import JournalEntryIn, JournalEntryOut
from app.modules.mental.services import diario_service

router = APIRouter()
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/journal-entries", response_model=list[JournalEntryOut])
def list_journal_entries(session: SessionDep) -> list[JournalEntry]:
    return diario_service.list_journal_entries(session)


@router.post(
    "/journal-entries", response_model=JournalEntryOut, status_code=status.HTTP_201_CREATED
)
def create_journal_entry(payload: JournalEntryIn, session: SessionDep) -> JournalEntry:
    return diario_service.create_journal_entry(session, payload)


@router.delete("/journal-entries/{entry_id}", status_code=NO_CONTENT)
def delete_journal_entry(entry_id: str, session: SessionDep) -> Response:
    diario_service.delete_journal_entry(session, entry_id)
    return Response(status_code=NO_CONTENT)
