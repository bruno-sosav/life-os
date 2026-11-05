import datetime as dt

from pydantic import BaseModel


class WeightPoint(BaseModel):
    date: dt.date
    kg: float


class ActivityCount(BaseModel):
    id: str
    name: str
    emoji: str | None
    color: str | None
    count: int  # días con la actividad en los últimos 30 días


class FinanceMonth(BaseModel):
    month: dt.date
    income: int
    expenses: int
    savings_pct: int | None
