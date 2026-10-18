import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, UTCDateTime

# Deben coincidir con CATEGORIES e INCOME_SOURCES de frontend/src/modules/finanzas
ExpenseCategory = Literal[
    "comida",
    "transporte",
    "salud",
    "ocio",
    "ropa",
    "educacion",
    "servicios",
    "suscripciones",
    "otro",
]
IncomeSource = Literal["sueldo", "freelance", "inversión", "regalo", "otro"]
Amount = Field(gt=0, lt=10**10)


class IncomeIn(BaseModel):
    month: dt.date  # cualquier día del mes; se guarda como el día 1
    amount: float = Amount
    source: IncomeSource | None = None
    notes: str | None = None


class IncomeOut(IncomeIn, ORMModel):
    id: str
    created_at: UTCDateTime


class ExpenseIn(BaseModel):
    date: dt.date
    amount: float = Amount
    category: ExpenseCategory
    description: str | None = None


class ExpenseOut(ExpenseIn, ORMModel):
    id: str
    created_at: UTCDateTime
