import datetime as dt

from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel, UTCDateTime


class JournalEntryIn(BaseModel):
    date: dt.date
    content: str = Field(min_length=1)
    mood_emoji: str | None = Field(default=None, max_length=32)


class JournalEntryOut(JournalEntryIn, ORMModel):
    id: str
    created_at: UTCDateTime
