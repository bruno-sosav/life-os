from datetime import date, timedelta

from app.modules.analytics.models.estadisticas_model import StatsInput
from app.modules.analytics.services import (
    indicadores_service,
)
from app.modules.mental import Skill
from tests.analytics.ayuda import MONDAY, TODAY, frame, habit, logs


def test_kpis() -> None:
    inp = StatsInput(
        today=TODAY,
        habits=[habit("h1")],
        habit_logs=logs(*[("h1", date(2026, 10, d)) for d in range(1, 10)]),
        weights=frame(["date", "kg"], [(date(2026, 9, 1), 82.0), (date(2026, 10, 15), 80.4)]),
        practices=frame(
            ["skill_id", "date", "minutes"],
            [("ingles", date(2026, 10, 3), 30), ("ingles", date(2026, 9, 28), 99)],
        ),
        workouts=frame(
            ["activity_id", "date"], [("gym", date(2026, 10, 2)), ("mma", date(2026, 9, 30))]
        ),
    )
    kpi = indicadores_service.kpis(inp)
    assert kpi["habit_month_pct"] == 50  # 9 de 18 días del mes
    assert (kpi["last_weight"], kpi["weight_trend"]) == (80.4, -1.6)
    # Solo lo del mes: la práctica de septiembre no suma
    assert (kpi["practice_month_minutes"], kpi["workouts_month"]) == (30, 1)


def test_habits_by_week_rows_keyed_by_habit_id() -> None:
    inp = StatsInput(
        today=TODAY, habits=[habit("h1"), habit("h2", "Agua")], habit_logs=logs(("h1", TODAY))
    )
    result = indicadores_service.habits_by_week(inp)
    assert [h["id"] for h in result["habits"]] == ["h1", "h2"]
    assert len(result["weeks"]) == 8
    assert result["weeks"][-1] == {"week_start": "2026-10-12", "h1": 1, "h2": 0}


def test_radar_mental_is_practice_against_weekly_goals() -> None:
    ingles = Skill(id="ingles", name="Inglés", stage="practicando", weekly_goal_min=120)
    ajedrez = Skill(id="ajedrez", name="Ajedrez", stage="practicando", weekly_goal_min=60)
    pausada = Skill(id="ciber", name="Ciber", stage="en_pausa", weekly_goal_min=500)  # no cuenta
    inp = StatsInput(
        today=TODAY,
        skills=[ingles, ajedrez, pausada],
        practices=frame(
            ["skill_id", "date", "minutes"],
            [("ingles", MONDAY, 60), ("ajedrez", MONDAY + timedelta(days=1), 30)],
        ),
    )
    radar = {r["axis"]: (r["semana"], r["anterior"]) for r in indicadores_service.radar(inp, 0)}
    assert list(radar) == ["Hábitos", "Entrenos", "Mental"]
    assert radar["Mental"] == (50, 0)  # 90 de 180 min


def test_skills_by_week() -> None:
    practicing = Skill(id="ingles", name="Inglés", stage="practicando")
    learned = Skill(id="vieja", name="Vieja", stage="la_tengo")  # ya la tenés y no practicaste
    inp = StatsInput(
        today=TODAY,
        skills=[practicing, learned],
        practices=frame(
            ["skill_id", "date", "minutes"], [("ingles", TODAY, 20), ("ingles", TODAY, 25)]
        ),
    )
    result = indicadores_service.skills_by_week(inp)
    assert result["skills"] == [{"id": "ingles", "name": "Inglés"}]
    assert len(result["weeks"]) == 8 and result["weeks"][-1]["ingles"] == 45
