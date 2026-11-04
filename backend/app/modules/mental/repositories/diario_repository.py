from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.mental.models.diario_model import JournalEntry


def list_journal_entries(session: Session) -> list[JournalEntry]:
    return list(session.scalars(select(JournalEntry).order_by(JournalEntry.created_at.desc())))
