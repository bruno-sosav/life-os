from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.core.fechas_util import month_bounds
from app.modules.finanzas import finanzas_repository as repository
from app.modules.finanzas.finanzas_model import FinanceExpense, FinanceIncome
from app.modules.finanzas.finanzas_schema import ExpenseIn, IncomeIn


# ─── Ingresos (se registran por mes) ────────────────────────
def list_income(session: Session, month: date) -> list[FinanceIncome]:
    return repository.list_income(session, month_bounds(month).start)


def create_income(session: Session, payload: IncomeIn) -> FinanceIncome:
    income = FinanceIncome(**payload.model_dump())
    income.month = month_bounds(payload.month).start
    return base_repository.save(session, income)


def delete_income(session: Session, income_id: str) -> None:
    base_repository.delete(session, get_or_404(session, FinanceIncome, income_id))


# ─── Gastos (se registran por día) ──────────────────────────
def list_expenses(session: Session, month: date) -> list[FinanceExpense]:
    return repository.list_expenses(session, *month_bounds(month))


def create_expense(session: Session, payload: ExpenseIn) -> FinanceExpense:
    return base_repository.save(session, FinanceExpense(**payload.model_dump()))


def delete_expense(session: Session, expense_id: str) -> None:
    base_repository.delete(session, get_or_404(session, FinanceExpense, expense_id))
