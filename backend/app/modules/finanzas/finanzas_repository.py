from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

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


def save[T: FinanceIncome | FinanceExpense](session: Session, record: T) -> T:
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def delete(session: Session, record: FinanceIncome | FinanceExpense) -> None:
    session.delete(record)
    session.commit()
