import datetime as dt

from pydantic import BaseModel, Field

from app.core.base_schema import Label, ORMModel, UTCDateTime

# Categorías y fuentes son libres: las elige el usuario ("🍔 Comida", "Sueldo"…)
Amount = Field(gt=0, lt=10**10)


class IncomeIn(BaseModel):
    month: dt.date  # cualquier día del mes; se guarda como el día 1
    amount: float = Amount
    source: Label | None = None
    notes: str | None = None


class IncomeOut(IncomeIn, ORMModel):
    id: str
    created_at: UTCDateTime


class ExpenseIn(BaseModel):
    date: dt.date
    amount: float = Amount
    category: Label
    description: str | None = None


class ExpenseOut(ExpenseIn, ORMModel):
    id: str
    created_at: UTCDateTime


# ─── Resumen del mes (GET /finance/summary) ─────────────────
class CategoryTotal(BaseModel):
    category: str
    total: float
    pct: float  # parte del gasto del mes, de 0 a 100


class MonthSummary(BaseModel):
    month: dt.date  # primer día del mes
    income: float
    expenses: float
    savings: float  # ingresos - gastos (puede ser negativo)
    savings_pct: int | None  # % del ingreso que queda; None sin ingresos
    spent_pct: int | None  # % del ingreso que se gastó, con tope 100; None sin ingresos
    by_category: list[CategoryTotal]  # de la que más gasto a la que menos


class Labels(BaseModel):
    """Categorías y fuentes en uso, de la más usada a la menos (para elegir al cargar)."""

    expense_categories: list[str]
    income_sources: list[str]
