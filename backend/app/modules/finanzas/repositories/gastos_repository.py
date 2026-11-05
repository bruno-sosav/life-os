from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.finanzas.models.gastos_model import FinanceExpense


def list_expenses(session: Session, first: date, last: date) -> list[FinanceExpense]:
    query = (
        select(FinanceExpense)
        .where(FinanceExpense.date.between(first, last))
        .order_by(FinanceExpense.date.desc(), FinanceExpense.created_at.desc())
    )
    return list(session.scalars(query))
