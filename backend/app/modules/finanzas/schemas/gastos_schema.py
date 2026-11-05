import datetime as dt

from pydantic import BaseModel

from app.core.base_schema import Amount, Label, ORMModel, UTCDateTime


class ExpenseIn(BaseModel):
    date: dt.date
    amount: float = Amount
    category: Label  # libre: la elige el usuario ("🍔 Comida"…)
    description: str | None = None


class ExpenseOut(ExpenseIn, ORMModel):
    id: str
    created_at: UTCDateTime
