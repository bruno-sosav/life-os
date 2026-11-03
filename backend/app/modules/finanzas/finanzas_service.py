from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.core.fechas_util import month_bounds
from app.core.numeros_util import js_round
from app.modules.finanzas import finanzas_repository as repository
from app.modules.finanzas.finanzas_model import FinanceExpense, FinanceIncome
from app.modules.finanzas.finanzas_schema import (
    CategoryTotal,
    ExpenseIn,
    IncomeIn,
    Labels,
    MonthSummary,
)


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


# ─── Resumen del mes ────────────────────────────────────────
def month_summary(session: Session, month: date) -> MonthSummary:
    """Totales, ahorro y gasto por categoría del mes que contiene `month`."""
    income = sum(float(i.amount) for i in list_income(session, month))
    expenses = list_expenses(session, month)
    spent = sum(float(e.amount) for e in expenses)
    by_category: dict[str, float] = {}
    for e in expenses:
        by_category[e.category] = by_category.get(e.category, 0.0) + float(e.amount)
    return MonthSummary(
        month=month_bounds(month).start,
        income=income,
        expenses=spent,
        savings=income - spent,
        savings_pct=js_round((income - spent) / income * 100) if income > 0 else None,
        spent_pct=min(100, js_round(spent / income * 100)) if income > 0 else None,
        by_category=[
            CategoryTotal(category=c, total=total, pct=round(total / spent * 100, 1))
            for c, total in sorted(by_category.items(), key=lambda kv: -kv[1])
        ],
    )


def labels(session: Session) -> Labels:
    return Labels(
        expense_categories=base_repository.used_labels(session, FinanceExpense.category),
        income_sources=base_repository.used_labels(session, FinanceIncome.source),
    )
