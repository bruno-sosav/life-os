"""KPIs del mes, radar de la semana y hábitos cumplidos por semana."""

from datetime import timedelta
from typing import Any

from app.core.fechas_util import Period, week_bounds
from app.core.numeros_util import js_round
from app.modules.analytics.models.estadisticas_model import StatsInput, between, ts
from app.modules.analytics.services.cumplimiento_service import (
    daily_status,
    done_habits,
    expected_habits,
)
from app.modules.rutina import streaks

WORKOUT_GOAL = 5  # días de entreno por semana que llenan el eje del radar

HABIT_WEEKS = 8


def kpis(inp: StatsInput) -> dict[str, Any]:
    today = inp.today
    month_start = today.replace(day=1)
    current_streak, best_streak = streaks(daily_status(inp))

    expected_month = expected_habits(inp.habits, month_start, today)
    done_month = done_habits(inp, month_start, today)
    habit_month_pct = js_round(done_month / expected_month * 100) if expected_month else 0

    weights = inp.weights.sort_values("date")
    last_weight = float(weights["kg"].iloc[-1]) if len(weights) else None
    older = weights[weights["date"] <= ts(today - timedelta(days=30))]
    weight_trend = (
        round(last_weight - float(older["kg"].iloc[-1]), 1)
        if last_weight is not None and len(older)
        else None
    )

    return {
        "current_streak": current_streak,
        "best_streak": best_streak,
        "workouts_month": len(between(inp.workouts, month_start, today)),
        "habit_month_pct": habit_month_pct,
        "last_weight": last_weight,
        "weight_trend": weight_trend,
        "practice_month_minutes": int(between(inp.practices, month_start, today)["minutes"].sum()),
    }


def habits_by_week(inp: StatsInput) -> dict[str, Any]:
    """Hábitos completados por hábito en ventanas de 7 días que terminan hoy, hace 7, 14…"""
    if not inp.habits:
        return {"habits": [], "weeks": []}
    weeks = []
    for w in range(HABIT_WEEKS - 1, -1, -1):
        end = inp.today - timedelta(days=w * 7)
        start = end - timedelta(days=6)
        counts = between(inp.habit_logs, start, end)["habit_id"].value_counts()
        row: dict[str, Any] = {"week_start": start.isoformat()}
        row.update({h.id: int(counts.get(h.id, 0)) for h in inp.habits})
        weeks.append(row)
    return {
        "habits": [{"id": h.id, "name": h.name, "color": h.color} for h in inp.habits],
        "weeks": weeks,
    }


def skills_by_week(inp: StatsInput) -> dict[str, Any]:
    """Minutos de práctica por skill en ventanas de 7 días que terminan hoy, hace 7, 14…

    Entran las skills que estás practicando y las que tuvieron práctica en esas semanas.
    """
    first = inp.today - timedelta(days=HABIT_WEEKS * 7 - 1)
    recent = set(between(inp.practices, first, inp.today)["skill_id"])
    skills = [s for s in inp.skills if s.stage == "practicando" or s.id in recent]
    weeks = []
    for w in range(HABIT_WEEKS - 1, -1, -1):
        end = inp.today - timedelta(days=w * 7)
        start = end - timedelta(days=6)
        totals = between(inp.practices, start, end).groupby("skill_id")["minutes"].sum()
        row: dict[str, Any] = {"week_start": start.isoformat()}
        row.update({s.id: int(totals.get(s.id, 0)) for s in skills})
        weeks.append(row)
    return {"skills": [{"id": s.id, "name": s.name} for s in skills], "weeks": weeks}


def _radar_metrics(inp: StatsInput, week: Period) -> dict[str, int]:
    expected = expected_habits(inp.habits, week.start, week.end)
    done = done_habits(inp, week.start, week.end)
    workouts = len(between(inp.workouts, week.start, week.end))
    practiced = int(between(inp.practices, week.start, week.end)["minutes"].sum())
    # La meta de Mental es la suma de las metas semanales de lo que estás practicando
    goal = sum(s.weekly_goal_min or 0 for s in inp.skills if s.stage == "practicando")
    return {
        "Hábitos": js_round(done / expected * 100) if expected else 0,
        "Entrenos": js_round(min(workouts / WORKOUT_GOAL, 1) * 100),
        "Mental": js_round(min(practiced / goal, 1) * 100) if goal else 0,
    }


def radar(inp: StatsInput, week_offset: int) -> list[dict[str, Any]]:
    current = _radar_metrics(inp, week_bounds(inp.today, week_offset))
    previous = _radar_metrics(inp, week_bounds(inp.today, week_offset + 1))
    return [{"axis": k, "semana": current[k], "anterior": previous[k]} for k in current]
