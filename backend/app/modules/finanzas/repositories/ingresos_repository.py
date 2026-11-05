from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.finanzas.models.ingresos_model import FinanceIncome


def list_income(session: Session, month: date) -> list[FinanceIncome]:
    query = (
        select(FinanceIncome).where(FinanceIncome.month == month).order_by(FinanceIncome.created_at)
    )
    return list(session.scalars(query))
