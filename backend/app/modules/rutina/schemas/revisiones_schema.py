from datetime import date

from pydantic import BaseModel

from app.core.base_schema import ORMModel, UTCDateTime


class WeeklyReviewIn(BaseModel):
    went_well: str | None = None
    would_change: str | None = None


class WeeklyReviewOut(WeeklyReviewIn, ORMModel):
    id: str
    week_start: date
    created_at: UTCDateTime
