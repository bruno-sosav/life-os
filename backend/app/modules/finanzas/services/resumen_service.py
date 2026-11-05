from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.fechas_util import month_bounds
from app.core.numeros_util import js_round
from app.modules.finanzas.models.gastos_model import FinanceExpense
from app.modules.finanzas.models.ingresos_model import FinanceIncome
from app.modules.finanzas.schemas.resumen_schema import CategoryTotal, Labels, MonthSummary
from app.modules.finanzas.services import gastos_service, ingresos_service


def month_summary(session: Session, month: date) -> MonthSummary:
    """Totales, ahorro y gasto por categoría del mes que contiene `month`."""
    income = sum(float(i.amount) for i in ingresos_service.list_income(session, month))
    expenses = gastos_service.list_expenses(session, month)
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
