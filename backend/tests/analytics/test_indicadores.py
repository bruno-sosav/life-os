from datetime import date, timedelta

from app.modules.analytics.models.estadisticas_model import StatsInput
from app.modules.analytics.services import (
    indicadores_service,
)
from tests.analytics.ayuda import MONDAY, TODAY, frame, habit, logs


def test_kpis() -> None:
    inp = StatsInput(
        today=TODAY,
        habits=[habit("h1")],
        habit_logs=logs(*[("h1", date(2026, 10, d)) for d in range(1, 10)]),
        weights=frame(["date", "kg"], [(date(2026, 9, 1), 82.0), (date(2026, 10, 15), 80.4)]),
        books_finished=[date(2026, 3, 1), date(2025, 12, 31)],
        workouts=frame(
            ["activity_id", "date"], [("gym", date(2026, 10, 2)), ("mma", date(2026, 9, 30))]
        ),
    )
    kpi = indicadores_service.kpis(inp)
    assert kpi["habit_month_pct"] == 50  # 9 de 18 días del mes
    assert (kpi["last_weight"], kpi["weight_trend"]) == (80.4, -1.6)
    assert (kpi["year"], kpi["books_year"], kpi["workouts_month"]) == (2026, 1, 1)


def test_habits_by_week_rows_keyed_by_habit_id() -> None:
    inp = StatsInput(
        today=TODAY, habits=[habit("h1"), habit("h2", "Agua")], habit_logs=logs(("h1", TODAY))
    )
    result = indicadores_service.habits_by_week(inp)
    assert [h["id"] for h in result["habits"]] == ["h1", "h2"]
    assert len(result["weeks"]) == 8
    assert result["weeks"][-1] == {"week_start": "2026-10-12", "h1": 1, "h2": 0}


def test_radar_axes_and_mental() -> None:
    inp = StatsInput(
        today=TODAY,
        journal=frame(["date"], [(MONDAY,), (MONDAY,)]),
        moods=frame(["date", "mood", "sleep"], [(MONDAY + timedelta(days=1), 4, 7.0)]),
    )
    radar = {r["axis"]: (r["semana"], r["anterior"]) for r in indicadores_service.radar(inp, 0)}
    assert list(radar) == ["Hábitos", "Entrenos", "Mental"]
    assert radar["Mental"] == (29, 0)  # 2 de 7 días
