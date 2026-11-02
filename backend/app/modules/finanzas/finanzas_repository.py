from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import InstrumentedAttribute, Session

from app.modules.finanzas.finanzas_model import FinanceExpense, FinanceIncome


def list_income(session: Session, month: date) -> list[FinanceIncome]:
    query = (
        select(FinanceIncome).where(FinanceIncome.month == month).order_by(FinanceIncome.created_at)
    )
    return list(session.scalars(query))


def list_expenses(session: Session, first: date, last: date) -> list[FinanceExpense]:
    query = (
        select(FinanceExpense)
        .where(FinanceExpense.date.between(first, last))
        .order_by(FinanceExpense.date.desc(), FinanceExpense.created_at.desc())
    )
    return list(session.scalars(query))


def used_labels(session: Session, column: InstrumentedAttribute[str | None]) -> list[str]:
    """Valores distintos de `column` en uso, de el más usado al menos."""
    count = func.count()
    query = (
        select(column).where(column.is_not(None)).group_by(column).order_by(count.desc(), column)
    )
    return [value for value in session.scalars(query) if value]
