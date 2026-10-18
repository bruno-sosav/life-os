import calendar
from datetime import date

from fastapi import APIRouter, Response, status
from sqlalchemy import select

from app.db import SessionDep
from app.models import FinanceExpense, FinanceIncome
from app.routers.common import get_or_404
from app.schemas.finanzas import ExpenseIn, ExpenseOut, IncomeIn, IncomeOut

router = APIRouter(prefix="/finance", tags=["finanzas"])


def _month_bounds(day: date) -> tuple[date, date]:
    last = calendar.monthrange(day.year, day.month)[1]
    return day.replace(day=1), day.replace(day=last)


# ─── Ingresos (se registran por mes) ────────────────────────
@router.get("/income", response_model=list[IncomeOut])
def list_income(month: date, session: SessionDep) -> list[FinanceIncome]:
    first, _ = _month_bounds(month)
    query = (
        select(FinanceIncome).where(FinanceIncome.month == first).order_by(FinanceIncome.created_at)
    )
    return list(session.scalars(query))


@router.post("/income", response_model=IncomeOut, status_code=status.HTTP_201_CREATED)
def create_income(payload: IncomeIn, session: SessionDep) -> FinanceIncome:
    income = FinanceIncome(**payload.model_dump())
    income.month = _month_bounds(payload.month)[0]
    session.add(income)
    session.commit()
    session.refresh(income)
    return income


@router.delete("/income/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(income_id: str, session: SessionDep) -> Response:
    session.delete(get_or_404(session, FinanceIncome, income_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─── Gastos (se registran por día) ──────────────────────────
@router.get("/expenses", response_model=list[ExpenseOut])
def list_expenses(month: date, session: SessionDep) -> list[FinanceExpense]:
    first, last = _month_bounds(month)
    query = (
        select(FinanceExpense)
        .where(FinanceExpense.date.between(first, last))
        .order_by(FinanceExpense.date.desc(), FinanceExpense.created_at.desc())
    )
    return list(session.scalars(query))


@router.post("/expenses", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseIn, session: SessionDep) -> FinanceExpense:
    expense = FinanceExpense(**payload.model_dump())
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: str, session: SessionDep) -> Response:
    session.delete(get_or_404(session, FinanceExpense, expense_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
