"""Series para los gráficos: peso, mood, actividades y finanzas."""

from datetime import date, timedelta
from typing import Any

import pandas as pd

from app.core.numeros_util import js_round
from app.modules.analytics.models.estadisticas_model import StatsInput, between

FINANCE_MONTHS = 6


def weight_series(inp: StatsInput) -> list[dict[str, Any]]:
    weights = inp.weights.sort_values("date").tail(90)
    return [
        {"date": day, "kg": float(kg)}
        for day, kg in zip(weights["date"].dt.date, weights["kg"].tolist(), strict=True)
    ]


def activity_distribution(inp: StatsInput) -> list[dict[str, Any]]:
    """Días de cada actividad en los últimos 30 días, de la más hecha a la menos."""
    recent = between(inp.workouts, inp.today - timedelta(days=30), inp.today)
    counts = recent["activity_id"].value_counts()
    rows = [
        {"id": a.id, "name": a.name, "emoji": a.emoji, "color": a.color, "count": int(counts[a.id])}
        for a in inp.activities
        if a.id in counts
    ]
    return sorted(rows, key=lambda r: -r["count"])


def months_back(today: date, months: int) -> date:
    total = today.year * 12 + today.month - 1 - months
    return date(total // 12, total % 12 + 1, 1)


def finance_monthly(inp: StatsInput) -> list[dict[str, Any]]:
    """Ingresos, gastos y % de ahorro de los últimos 6 meses (incluye el actual)."""
    income = inp.income.groupby(inp.income["month"].dt.to_period("M"))["amount"].sum()
    expenses = inp.expenses.groupby(inp.expenses["date"].dt.to_period("M"))["amount"].sum()
    months = []
    for back in range(FINANCE_MONTHS - 1, -1, -1):
        first = months_back(inp.today, back)
        period = pd.Period(first, freq="M")
        inc = float(income.get(period, 0.0))
        exp = float(expenses.get(period, 0.0))
        months.append(
            {
                "month": first,
                "income": js_round(inc),
                "expenses": js_round(exp),
                "savings_pct": js_round((inc - exp) / inc * 100) if inc > 0 else None,
            }
        )
    return months
