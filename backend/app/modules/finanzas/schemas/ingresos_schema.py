import datetime as dt

from pydantic import BaseModel

from app.core.base_schema import Amount, Label, ORMModel, UTCDateTime


class IncomeIn(BaseModel):
    month: dt.date  # cualquier día del mes; se guarda como el día 1
    amount: float = Amount
    source: Label | None = None  # libre: "Sueldo", "Freelance"…
    notes: str | None = None


class IncomeOut(IncomeIn, ORMModel):
    id: str
    created_at: UTCDateTime
