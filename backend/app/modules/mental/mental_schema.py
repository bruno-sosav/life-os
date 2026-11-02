import datetime as dt
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

from app.core.base_schema import ORMModel, UTCDateTime

# Los estados de libro quedan fijos: "leido" tiene reglas (cuenta en Stats)
BookStatus = Literal["pendiente", "leyendo", "leido"]
# Las etiquetas de ideas son libres: se ven tal cual, emoji incluido ("💬 Frase")
IdeaTag = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]
DEFAULT_TAG = "💡 Idea"
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


class Shelves(BaseModel):
    pendiente: list[BookOut]
    leyendo: list[BookOut]
    leido: list[BookOut]


class Library(BaseModel):
    shelves: Shelves
    year: int
    read_this_year: int  # leídos con fecha de fin en el año de `today`


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


class MoodAverage(BaseModel):
    avg_mood: float | None  # promedio de los últimos 7 días, o None sin registros


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
    tag: IdeaTag = DEFAULT_TAG


class IdeaOut(IdeaIn, ORMModel):
    id: str
    created_at: UTCDateTime


class TagCount(BaseModel):
    tag: str
    count: int
