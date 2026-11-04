import datetime as dt

from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel, UTCDateTime


class GoalIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    month: dt.date  # cualquier día del mes; se guarda como el día 1


class GoalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    progress: int | None = Field(default=None, ge=0, le=100)


class GoalOut(ORMModel):
    id: str
    title: str
    month: dt.date
    progress: int
    completed: bool
    created_at: UTCDateTime
