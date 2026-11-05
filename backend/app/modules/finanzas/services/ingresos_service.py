from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.core.fechas_util import month_bounds
from app.modules.finanzas.models.ingresos_model import FinanceIncome
from app.modules.finanzas.repositories import ingresos_repository
from app.modules.finanzas.schemas.ingresos_schema import IncomeIn


def list_income(session: Session, month: date) -> list[FinanceIncome]:
    return ingresos_repository.list_income(session, month_bounds(month).start)


def create_income(session: Session, payload: IncomeIn) -> FinanceIncome:
    income = FinanceIncome(**payload.model_dump())
    income.month = month_bounds(payload.month).start
    return base_repository.save(session, income)


def delete_income(session: Session, income_id: str) -> None:
    base_repository.delete(session, get_or_404(session, FinanceIncome, income_id))
