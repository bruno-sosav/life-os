import datetime as dt

from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel, UTCDateTime


class WeightLogIn(BaseModel):
    weight_kg: float = Field(gt=0, lt=1000)
    notes: str | None = None


class WeightLogOut(WeightLogIn, ORMModel):
    id: str
    date: dt.date
    created_at: UTCDateTime


class WeightGoalIn(BaseModel):
    weight_kg: float | None = Field(gt=0, lt=1000)  # None = sin meta
