from datetime import date

from app.modules.analytics.models.estadisticas_model import StatsInput
from app.modules.analytics.services import (
    resumen_service,
    series_service,
)
from app.modules.fisico import Activity
from tests.analytics.ayuda import TODAY, frame


def test_finance_monthly() -> None:
    inp = StatsInput(
        today=TODAY,
        income=frame(["month", "amount"], [(date(2026, 10, 1), 1000.0), (date(2026, 4, 1), 50.0)]),
        expenses=frame(["date", "amount"], [(date(2026, 10, 5), 250.4), (date(2026, 9, 2), 30.0)]),
    )
    months = series_service.finance_monthly(inp)
    assert [m["month"] for m in months] == [date(2026, m, 1) for m in range(5, 11)]
    assert months[-1] == {
        "month": date(2026, 10, 1),
        "income": 1000,
        "expenses": 250,
        "savings_pct": 75,
    }
    assert months[-2]["savings_pct"] is None  # sin ingresos


def test_activity_distribution_includes_paused_with_sessions() -> None:
    gym = Activity(id="gym", name="Gym", emoji=None, color="#fff", active=True)
    mma = Activity(id="mma", name="MMA", emoji=None, color="#f00", active=False)
    run = Activity(id="run", name="Correr", emoji=None, color="#0f0", active=True)
    inp = StatsInput(
        today=TODAY,
        activities=[run, gym, mma],
        workouts=frame(
            ["activity_id", "date"],
            [("gym", TODAY), ("gym", TODAY), ("mma", TODAY), ("gym", date(2026, 1, 1))],
        ),
    )
    rows = series_service.activity_distribution(inp)
    # Correr no tuvo sesiones: no aparece. MMA está pausada pero se usó: aparece.
    assert [(r["name"], r["count"]) for r in rows] == [("Gym", 2), ("MMA", 1)]


def test_series_empty_inputs() -> None:
    inp = StatsInput(today=TODAY)
    result = resumen_service.summary(inp, 0)
    assert result["weight_series"] == [] and result["skills_by_week"]["skills"] == []
    assert result["compliance"]["pct"] is None and result["compliance"]["delta"] is None
    assert result["kpis"]["current_streak"] == 0
