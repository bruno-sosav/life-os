from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import EMOJI, NAME, STATUS, Base, CreatedAt, UUIDPk


class Book(UUIDPk, CreatedAt, Base):
    __tablename__ = "books"
    __table_args__ = (CheckConstraint("rating BETWEEN 1 AND 5", name="rating"),)

    title: Mapped[str] = mapped_column(String(NAME))
    author: Mapped[str | None] = mapped_column(String(NAME))
    status: Mapped[str] = mapped_column(String(STATUS), default="pendiente")
    rating: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[date | None] = mapped_column(Date)
    finished_at: Mapped[date | None] = mapped_column(Date)


class MoodLog(UUIDPk, CreatedAt, Base):
    __tablename__ = "mood_logs"
    __table_args__ = (
        CheckConstraint("mood_score BETWEEN 1 AND 5", name="mood_score"),
        CheckConstraint("energy_score BETWEEN 1 AND 5", name="energy_score"),
    )

    date: Mapped[date] = mapped_column(Date, unique=True)
    mood_score: Mapped[int | None] = mapped_column(Integer)
    sleep_hours: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    energy_score: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)


class JournalEntry(UUIDPk, CreatedAt, Base):
    __tablename__ = "journal_entries"

    date: Mapped[date] = mapped_column(Date, index=True)
    content: Mapped[str] = mapped_column(Text)
    mood_emoji: Mapped[str | None] = mapped_column(String(EMOJI))


class Idea(UUIDPk, CreatedAt, Base):
    __tablename__ = "ideas"

    text: Mapped[str] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(String(NAME))
    # 'idea' | 'frase' | 'idea de negocio' | 'aprendizaje' | 'meta'
    tag: Mapped[str] = mapped_column(String(STATUS), default="idea")
