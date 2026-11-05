import datetime as dt

from pydantic import BaseModel


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
