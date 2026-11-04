from datetime import date

from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import EMOJI, Base, CreatedAt, UUIDPk


class JournalEntry(UUIDPk, CreatedAt, Base):
    __tablename__ = "journal_entries"

    date: Mapped[date] = mapped_column(Date, index=True)
    content: Mapped[str] = mapped_column(Text)
    mood_emoji: Mapped[str | None] = mapped_column(String(EMOJI))
