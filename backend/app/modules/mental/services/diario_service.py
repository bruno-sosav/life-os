from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.modules.mental.models.diario_model import JournalEntry
from app.modules.mental.repositories import diario_repository
from app.modules.mental.schemas.diario_schema import JournalEntryIn


def list_journal_entries(session: Session) -> list[JournalEntry]:
    return diario_repository.list_journal_entries(session)


def create_journal_entry(session: Session, payload: JournalEntryIn) -> JournalEntry:
    return base_repository.save(session, JournalEntry(**payload.model_dump()))


def delete_journal_entry(session: Session, entry_id: str) -> None:
    base_repository.delete(session, get_or_404(session, JournalEntry, entry_id))
