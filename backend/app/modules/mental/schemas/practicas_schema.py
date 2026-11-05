import datetime as dt

from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel, UTCDateTime


class PracticeIn(BaseModel):
    skill_id: str
    date: dt.date
    minutes: int = Field(ge=1, le=24 * 60)
    note: str | None = Field(default=None, max_length=2000)


class PracticeOut(PracticeIn, ORMModel):
    id: str
    created_at: UTCDateTime
