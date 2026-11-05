from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.core.fechas_util import month_bounds
from app.modules.finanzas.models.gastos_model import FinanceExpense
from app.modules.finanzas.repositories import gastos_repository
from app.modules.finanzas.schemas.gastos_schema import ExpenseIn


def list_expenses(session: Session, month: date) -> list[FinanceExpense]:
    return gastos_repository.list_expenses(session, *month_bounds(month))


def create_expense(session: Session, payload: ExpenseIn) -> FinanceExpense:
    return base_repository.save(session, FinanceExpense(**payload.model_dump()))


def delete_expense(session: Session, expense_id: str) -> None:
    base_repository.delete(session, get_or_404(session, FinanceExpense, expense_id))
