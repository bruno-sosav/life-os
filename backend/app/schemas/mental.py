import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, UTCDateTime

BookStatus = Literal["pendiente", "leyendo", "leido"]
IdeaTag = Literal["idea", "frase", "idea de negocio", "aprendizaje", "meta"]
Score = Field(default=None, ge=1, le=5)


# ─── Libros ─────────────────────────────────────────────────
class BookIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str | None = Field(default=None, max_length=255)
    status: BookStatus = "pendiente"
    rating: int | None = Score
    notes: str | None = None
    started_at: dt.date | None = None
    finished_at: dt.date | None = None


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, max_length=255)
    status: BookStatus | None = None
    rating: int | None = Score
    notes: str | None = None
    started_at: dt.date | None = None
    finished_at: dt.date | None = None


class BookOut(BookIn, ORMModel):
    id: str
    created_at: UTCDateTime


# ─── Mood ───────────────────────────────────────────────────
class MoodLogIn(BaseModel):
    mood_score: int | None = Score
    energy_score: int | None = Score
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    notes: str | None = None


class MoodLogOut(MoodLogIn, ORMModel):
    id: str
    date: dt.date
    created_at: UTCDateTime


# ─── Diario ─────────────────────────────────────────────────
class JournalEntryIn(BaseModel):
    date: dt.date
    content: str = Field(min_length=1)
    mood_emoji: str | None = Field(default=None, max_length=32)


class JournalEntryOut(JournalEntryIn, ORMModel):
    id: str
    created_at: UTCDateTime


# ─── Ideas ──────────────────────────────────────────────────
class IdeaIn(BaseModel):
    text: str = Field(min_length=1)
    author: str | None = Field(default=None, max_length=255)
    tag: IdeaTag = "idea"


class IdeaOut(IdeaIn, ORMModel):
    id: str
    created_at: UTCDateTime
