from datetime import date, timedelta

from app.core.fechas_util import Period, month_bounds, week_bounds
from app.core.numeros_util import js_round
from app.modules.analytics.models.estadisticas_model import StatsInput
from app.modules.analytics.services import (
    cumplimiento_service,
    indicadores_service,
)
from app.modules.rutina import RoutineBlock
from tests.analytics.ayuda import MONDAY, TODAY, frame, habit, logs


def test_js_round_and_date_bounds() -> None:
    assert (js_round(2.5), js_round(2.4), js_round(-0.5)) == (3, 2, 0)
    assert week_bounds(TODAY) == Period(MONDAY, TODAY)
    assert week_bounds(TODAY, 1).start == MONDAY - timedelta(days=7)
    assert month_bounds(date(2028, 2, 10)) == Period(date(2028, 2, 1), date(2028, 2, 29))


def test_week_compliance_counts_habits_and_blocks() -> None:
    block = RoutineBlock(id="b1", activity="Leer", days_of_week=[0], repeat_weekly=True)
    inp = StatsInput(
        today=TODAY,
        habits=[habit("h1"), habit("h2", "Finde", days=[5])],
        blocks=[block],
        # h2 se hizo el lunes, que no le tocaba: no tapa lo que faltó otros días
        habit_logs=logs(*[("h1", MONDAY + timedelta(days=i)) for i in range(3)], ("h2", MONDAY)),
        completions=frame(["block_id", "date"], [("b1", MONDAY)]),
    )
    result = cumplimiento_service.compliance(inp, 0)
    # Agendado: h1 x7 + h2 el sábado + b1 el lunes = 9. Hecho: lunes 2 (tope), martes 1, miércoles 1
    assert (result["done"], result["expected"], result["pct"]) == (4, 9, 44)
    assert (result["prev_pct"], result["delta"]) == (0, 44)


def test_week_compliance_counts_only_until_today() -> None:
    wednesday = MONDAY + timedelta(days=2)
    inp = StatsInput(
        today=wednesday, habits=[habit("h1")], habit_logs=logs(("h1", MONDAY), ("h1", wednesday))
    )
    assert (
        cumplimiento_service.week_compliance(inp, week_bounds(wednesday))["pct"] == 67
    )  # 2 de 3 días
    future = week_bounds(wednesday + timedelta(days=7))
    assert cumplimiento_service.week_compliance(inp, future)["pct"] is None


def test_compliance_history_has_12_weeks() -> None:
    inp = StatsInput(today=TODAY, habits=[habit("h1")], habit_logs=logs(("h1", TODAY)))
    history = cumplimiento_service.compliance_history(inp)
    assert len(history) == 12 and history[-1]["is_current"]
    assert (history[-1]["week_start"], history[-1]["pct"]) == (MONDAY, 14)  # 1 de 7


def test_streaks_current_and_best() -> None:
    days = [TODAY - timedelta(days=n) for n in (1, 2, 3, 10, 11, 12, 13, 14)]
    inp = StatsInput(today=TODAY, habits=[habit("h1")], habit_logs=logs(*[("h1", d) for d in days]))
    assert indicadores_service.kpis(inp)["current_streak"] == 3  # hoy pendiente no corta
    assert indicadores_service.kpis(inp)["best_streak"] == 5

    inp.habit_logs = logs(*[("h1", d) for d in [TODAY, *days]])
    assert indicadores_service.kpis(inp)["current_streak"] == 4


def test_heatmap_grid_and_status() -> None:
    inp = StatsInput(
        today=TODAY,
        habits=[habit("h1"), habit("h2", "Agua")],
        habit_logs=logs(("h1", TODAY), ("h2", TODAY), ("h1", TODAY - timedelta(1))),
    )
    result = cumplimiento_service.heatmap(inp)
    cells = result["cells"]
    real = [c for c in cells if c["date"] is not None]
    assert len(cells) % 7 == 0 and len(real) == 90
    first = TODAY - timedelta(days=89)
    assert cells[: first.weekday()] == [{"date": None, "status": None}] * first.weekday()
    assert [c["status"] for c in real[-3:]] == ["sin_cumplir", "parcial", "cumplido"]
    assert (result["cumplido"], result["parcial"], result["sin_cumplir"]) == (1, 1, 88)
