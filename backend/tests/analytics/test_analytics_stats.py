from datetime import date, timedelta

import pandas as pd

from app.core.fechas_util import Period, month_bounds, week_bounds
from app.core.numeros_util import js_round
from app.modules.analytics import analytics_service as stats
from app.modules.fisico import Activity
from app.modules.rutina import Habit, RoutineBlock

TODAY = date(2026, 10, 18)  # domingo
MONDAY = date(2026, 10, 12)


def frame(columns: list[str], rows: list[tuple[object, ...]]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=columns)
    for column in ("date", "month"):
        if column in df:
            df[column] = pd.to_datetime(df[column])
    return df


def habit(id_: str, name: str = "Leer", days: list[int] | None = None) -> Habit:
    return Habit(id=id_, name=name, color="#fff", days_of_week=days)


def logs(*items: tuple[str, date]) -> pd.DataFrame:
    return frame(["habit_id", "date"], list(items))


def test_js_round_and_date_bounds() -> None:
    assert (js_round(2.5), js_round(2.4), js_round(-0.5)) == (3, 2, 0)
    assert week_bounds(TODAY) == Period(MONDAY, TODAY)
    assert week_bounds(TODAY, 1).start == MONDAY - timedelta(days=7)
    assert month_bounds(date(2028, 2, 10)) == Period(date(2028, 2, 1), date(2028, 2, 29))


def test_week_compliance_counts_habits_and_blocks() -> None:
    block = RoutineBlock(id="b1", activity="Leer", days_of_week=[0], repeat_weekly=True)
    inp = stats.StatsInput(
        today=TODAY,
        habits=[habit("h1"), habit("h2", "Finde", days=[5])],
        blocks=[block],
        # h2 se hizo el lunes, que no le tocaba: no tapa lo que faltó otros días
        habit_logs=logs(*[("h1", MONDAY + timedelta(days=i)) for i in range(3)], ("h2", MONDAY)),
        completions=frame(["block_id", "date"], [("b1", MONDAY)]),
    )
    result = stats.compliance(inp, 0)
    # Agendado: h1 x7 + h2 el sábado + b1 el lunes = 9. Hecho: lunes 2 (tope), martes 1, miércoles 1
    assert (result["done"], result["expected"], result["pct"]) == (4, 9, 44)
    assert (result["prev_pct"], result["delta"]) == (0, 44)


def test_week_compliance_counts_only_until_today() -> None:
    wednesday = MONDAY + timedelta(days=2)
    inp = stats.StatsInput(
        today=wednesday, habits=[habit("h1")], habit_logs=logs(("h1", MONDAY), ("h1", wednesday))
    )
    assert stats.week_compliance(inp, week_bounds(wednesday))["pct"] == 67  # 2 de 3 días
    future = week_bounds(wednesday + timedelta(days=7))
    assert stats.week_compliance(inp, future)["pct"] is None


def test_compliance_history_has_12_weeks() -> None:
    inp = stats.StatsInput(today=TODAY, habits=[habit("h1")], habit_logs=logs(("h1", TODAY)))
    history = stats.compliance_history(inp)
    assert len(history) == 12 and history[-1]["is_current"]
    assert (history[-1]["week_start"], history[-1]["pct"]) == (MONDAY, 14)  # 1 de 7


def test_streaks_current_and_best() -> None:
    days = [TODAY - timedelta(days=n) for n in (1, 2, 3, 10, 11, 12, 13, 14)]
    inp = stats.StatsInput(
        today=TODAY, habits=[habit("h1")], habit_logs=logs(*[("h1", d) for d in days])
    )
    assert stats.kpis(inp)["current_streak"] == 3  # hoy pendiente no corta
    assert stats.kpis(inp)["best_streak"] == 5

    inp.habit_logs = logs(*[("h1", d) for d in [TODAY, *days]])
    assert stats.kpis(inp)["current_streak"] == 4


def test_kpis() -> None:
    inp = stats.StatsInput(
        today=TODAY,
        habits=[habit("h1")],
        habit_logs=logs(*[("h1", date(2026, 10, d)) for d in range(1, 10)]),
        weights=frame(["date", "kg"], [(date(2026, 9, 1), 82.0), (date(2026, 10, 15), 80.4)]),
        books_finished=[date(2026, 3, 1), date(2025, 12, 31)],
        workouts=frame(
            ["activity_id", "date"], [("gym", date(2026, 10, 2)), ("mma", date(2026, 9, 30))]
        ),
    )
    kpi = stats.kpis(inp)
    assert kpi["habit_month_pct"] == 50  # 9 de 18 días del mes
    assert (kpi["last_weight"], kpi["weight_trend"]) == (80.4, -1.6)
    assert (kpi["year"], kpi["books_year"], kpi["workouts_month"]) == (2026, 1, 1)


def test_habits_by_week_rows_keyed_by_habit_id() -> None:
    inp = stats.StatsInput(
        today=TODAY, habits=[habit("h1"), habit("h2", "Agua")], habit_logs=logs(("h1", TODAY))
    )
    result = stats.habits_by_week(inp)
    assert [h["id"] for h in result["habits"]] == ["h1", "h2"]
    assert len(result["weeks"]) == 8
    assert result["weeks"][-1] == {"week_start": "2026-10-12", "h1": 1, "h2": 0}


def test_radar_axes_and_mental() -> None:
    inp = stats.StatsInput(
        today=TODAY,
        journal=frame(["date"], [(MONDAY,), (MONDAY,)]),
        moods=frame(["date", "mood", "sleep"], [(MONDAY + timedelta(days=1), 4, 7.0)]),
    )
    radar = {r["axis"]: (r["semana"], r["anterior"]) for r in stats.radar(inp, 0)}
    assert list(radar) == ["Hábitos", "Entrenos", "Mental"]
    assert radar["Mental"] == (29, 0)  # 2 de 7 días


def test_heatmap_grid_and_status() -> None:
    inp = stats.StatsInput(
        today=TODAY,
        habits=[habit("h1"), habit("h2", "Agua")],
        habit_logs=logs(("h1", TODAY), ("h2", TODAY), ("h1", TODAY - timedelta(1))),
    )
    result = stats.heatmap(inp)
    cells = result["cells"]
    real = [c for c in cells if c["date"] is not None]
    assert len(cells) % 7 == 0 and len(real) == 90
    first = TODAY - timedelta(days=89)
    assert cells[: first.weekday()] == [{"date": None, "status": None}] * first.weekday()
    assert [c["status"] for c in real[-3:]] == ["sin_cumplir", "parcial", "cumplido"]
    assert (result["cumplido"], result["parcial"], result["sin_cumplir"]) == (1, 1, 88)


def test_finance_monthly() -> None:
    inp = stats.StatsInput(
        today=TODAY,
        income=frame(["month", "amount"], [(date(2026, 10, 1), 1000.0), (date(2026, 4, 1), 50.0)]),
        expenses=frame(["date", "amount"], [(date(2026, 10, 5), 250.4), (date(2026, 9, 2), 30.0)]),
    )
    months = stats.finance_monthly(inp)
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
    inp = stats.StatsInput(
        today=TODAY,
        activities=[run, gym, mma],
        workouts=frame(
            ["activity_id", "date"],
            [("gym", TODAY), ("gym", TODAY), ("mma", TODAY), ("gym", date(2026, 1, 1))],
        ),
    )
    rows = stats.activity_distribution(inp)
    # Correr no tuvo sesiones: no aparece. MMA está pausada pero se usó: aparece.
    assert [(r["name"], r["count"]) for r in rows] == [("Gym", 2), ("MMA", 1)]


def test_series_empty_inputs() -> None:
    inp = stats.StatsInput(today=TODAY)
    result = stats.summary(inp, 0)
    assert result["weight_series"] == [] and result["mood_series"] == []
    assert result["compliance"]["pct"] is None and result["compliance"]["delta"] is None
    assert result["kpis"]["current_streak"] == 0
