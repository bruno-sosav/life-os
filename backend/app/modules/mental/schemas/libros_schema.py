import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel, Score, UTCDateTime

# Los estados de libro quedan fijos: "leido" tiene reglas (cuenta en Stats)
BookStatus = Literal["pendiente", "leyendo", "leido"]


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
