"""Estadísticas de la pantalla Stats: Score Bruce, KPIs, radar, heatmap y series.

Las funciones son puras: reciben los registros ya leídos de la base (en DataFrames con
una columna `date` de tipo datetime64) y devuelven estructuras listas para serializar.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Literal

import pandas as pd

from app.models import Habit, RoutineBlock
from app.services.dashboard import expected_per_day

BruceLevel = Literal["elite", "modo_bruce", "activando", "apagado"]

WORKOUT_GOAL = 5  # sesiones por semana que dan el puntaje completo
STRATUS_GOAL = 5  # días por semana con trabajo en Stratus
HEATMAP_DAYS = 90
HISTORY_WEEKS = 12
HABIT_WEEKS = 8
FINANCE_MONTHS = 6


def js_round(value: float) -> int:
    """Redondeo como Math.round de JS (2.5 → 3), para no cambiar los números históricos."""
    return math.floor(value + 0.5)


@dataclass(frozen=True)
class Week:
    start: date
    end: date


def week_bounds(today: date, offset: int = 0) -> Week:
    """Semana de lunes a domingo, `offset` semanas hacia atrás."""
    monday = today - timedelta(days=today.weekday() + 7 * offset)
    return Week(monday, monday + timedelta(days=6))


def _empty(*columns: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            c: pd.Series(dtype="datetime64[ns]" if c in ("date", "month") else "object")
            for c in columns
        }
    )


@dataclass
class StatsInput:
    today: date
    habits: Sequence[Habit] = ()
    blocks: Sequence[RoutineBlock] = ()
    # Hábitos completados (solo hábitos activos): habit_id, date
    habit_logs: pd.DataFrame = field(default_factory=lambda: _empty("habit_id", "date"))
    # Bloques completados: block_id, date
    completions: pd.DataFrame = field(default_factory=lambda: _empty("block_id", "date"))
    # Entrenos con asistencia: kind ('gym' | 'mma'), date
    workouts: pd.DataFrame = field(default_factory=lambda: _empty("kind", "date"))
    weights: pd.DataFrame = field(default_factory=lambda: _empty("date", "kg"))
    moods: pd.DataFrame = field(default_factory=lambda: _empty("date", "mood", "sleep"))
    journal: pd.DataFrame = field(default_factory=lambda: _empty("date"))
    books_finished: Sequence[date] = ()
    income: pd.DataFrame = field(default_factory=lambda: _empty("month", "amount"))
    expenses: pd.DataFrame = field(default_factory=lambda: _empty("date", "amount"))


def _ts(day: date) -> pd.Timestamp:
    return pd.Timestamp(day)


def _between(df: pd.DataFrame, start: date, end: date, column: str = "date") -> pd.DataFrame:
    return df[(df[column] >= _ts(start)) & (df[column] <= _ts(end))]


def _days(start: date, end: date) -> pd.DatetimeIndex:
    return pd.date_range(_ts(start), _ts(end), freq="D")


def _expected_habits(habits: Sequence[Habit], start: date, end: date) -> int:
    return int(expected_per_day(_days(start, end), [], habits).sum())


def _stratus_days(inp: StatsInput, week: Week) -> int:
    """Días de la semana con algún hábito o bloque de rutina 'Stratus' completado."""
    habit_ids = {h.id for h in inp.habits if "stratus" in (h.name or "").lower()}
    block_ids = {b.id for b in inp.blocks if "stratus" in (b.activity or "").lower()}
    logs = _between(inp.habit_logs, week.start, week.end)
    comps = _between(inp.completions, week.start, week.end)
    dates = pd.concat(
        [
            logs.loc[logs["habit_id"].isin(habit_ids), "date"],
            comps.loc[comps["block_id"].isin(block_ids), "date"],
        ]
    )
    return int(dates.nunique())


# ─── Score Bruce ────────────────────────────────────────────
def bruce_level(total: int) -> BruceLevel:
    if total >= 91:
        return "elite"
    if total >= 71:
        return "modo_bruce"
    if total >= 41:
        return "activando"
    return "apagado"


def bruce_score(inp: StatsInput, week: Week) -> dict[str, Any]:
    """Hábitos (50 pts) + entrenos (30 pts, meta 5/semana) + Stratus (20 pts, meta 5 días)."""
    expected = _expected_habits(inp.habits, week.start, week.end)
    completed = len(_between(inp.habit_logs, week.start, week.end))
    workouts = len(_between(inp.workouts, week.start, week.end))
    stratus_days = _stratus_days(inp, week)

    habit_score = js_round(min(completed / expected, 1) * 50) if expected else 0
    workout_score = js_round(min(workouts / WORKOUT_GOAL, 1) * 30)
    stratus_score = js_round(min(stratus_days / STRATUS_GOAL, 1) * 20)
    total = habit_score + workout_score + stratus_score
    return {
        "total": total,
        "level": bruce_level(total),
        "habit_score": habit_score,
        "workout_score": workout_score,
        "stratus_score": stratus_score,
        "completed_habits": completed,
        "expected_habits": expected,
        "workouts": workouts,
        "stratus_days": stratus_days,
    }


def bruce_history(inp: StatsInput) -> list[dict[str, Any]]:
    points = []
    for offset in range(HISTORY_WEEKS - 1, -1, -1):
        week = week_bounds(inp.today, offset)
        points.append(
            {
                "week_start": week.start,
                "score": bruce_score(inp, week)["total"],
                "is_current": offset == 0,
            }
        )
    return points


# ─── KPIs ───────────────────────────────────────────────────
def _daily_habit_counts(inp: StatsInput) -> pd.Series:
    """Hábitos completados por día en los últimos 90 días (incluye hoy)."""
    days = _days(inp.today - timedelta(days=HEATMAP_DAYS - 1), inp.today)
    counts = inp.habit_logs["date"].value_counts()
    return counts.reindex(days, fill_value=0).astype("int64")


def habit_streaks(inp: StatsInput) -> tuple[int, int]:
    """(racha actual, mejor racha) de días con al menos un hábito, en 90 días.

    Hoy sin hábitos todavía no corta la racha actual: el día no terminó.
    """
    active = _daily_habit_counts(inp) > 0
    run_id = (~active).cumsum()
    runs = active.groupby(run_id).cumsum()  # largo de la racha que termina en cada día
    best = int(runs.max()) if len(runs) else 0

    # Hoy sin hábitos: vale la racha que terminó ayer
    last = -1 if active.iloc[-1] or len(runs) == 1 else -2
    current = int(runs.iloc[last])
    return current, best


def kpis(inp: StatsInput) -> dict[str, Any]:
    today = inp.today
    month_start = today.replace(day=1)
    current_streak, best_streak = habit_streaks(inp)

    expected_month = _expected_habits(inp.habits, month_start, today)
    done_month = len(_between(inp.habit_logs, month_start, today))
    habit_month_pct = min(100, js_round(done_month / expected_month * 100)) if expected_month else 0

    weights = inp.weights.sort_values("date")
    last_weight = float(weights["kg"].iloc[-1]) if len(weights) else None
    older = weights[weights["date"] <= _ts(today - timedelta(days=30))]
    weight_trend = (
        round(last_weight - float(older["kg"].iloc[-1]), 1)
        if last_weight is not None and len(older)
        else None
    )

    return {
        "current_streak": current_streak,
        "best_streak": best_streak,
        "workouts_month": len(_between(inp.workouts, month_start, today)),
        "habit_month_pct": habit_month_pct,
        "last_weight": last_weight,
        "weight_trend": weight_trend,
        "year": today.year,
        "books_year": sum(1 for d in inp.books_finished if d.year == today.year),
    }


# ─── Hábitos por semana ─────────────────────────────────────
def habits_by_week(inp: StatsInput) -> dict[str, Any]:
    """Hábitos completados por hábito en ventanas de 7 días que terminan hoy, hace 7, 14…"""
    if not inp.habits:
        return {"habits": [], "weeks": []}
    weeks = []
    for w in range(HABIT_WEEKS - 1, -1, -1):
        end = inp.today - timedelta(days=w * 7)
        start = end - timedelta(days=6)
        counts = _between(inp.habit_logs, start, end)["habit_id"].value_counts()
        row: dict[str, Any] = {"week_start": start.isoformat()}
        row.update({h.id: int(counts.get(h.id, 0)) for h in inp.habits})
        weeks.append(row)
    return {
        "habits": [{"id": h.id, "name": h.name, "color": h.color} for h in inp.habits],
        "weeks": weeks,
    }


# ─── Radar semanal ──────────────────────────────────────────
def _radar_metrics(inp: StatsInput, week: Week) -> dict[str, int]:
    expected = _expected_habits(inp.habits, week.start, week.end)
    done = len(_between(inp.habit_logs, week.start, week.end))
    workouts = len(_between(inp.workouts, week.start, week.end))
    mental_dates = pd.concat(
        [
            _between(inp.journal, week.start, week.end)["date"],
            _between(inp.moods, week.start, week.end)["date"],
        ]
    ).nunique()
    has_finance = (
        len(_between(inp.expenses, week.start, week.end)) > 0
        or len(_between(inp.income, week.start, week.end, column="month")) > 0
    )
    return {
        "Hábitos": js_round(done / expected * 100) if expected else 0,
        "Entrenos": js_round(min(workouts / WORKOUT_GOAL, 1) * 100),
        "Stratus": js_round(min(_stratus_days(inp, week) / STRATUS_GOAL, 1) * 100),
        "Mental": js_round(min(mental_dates / 7, 1) * 100),
        "Finanzas": 100 if has_finance else 0,
    }


def radar(inp: StatsInput, week_offset: int) -> list[dict[str, Any]]:
    current = _radar_metrics(inp, week_bounds(inp.today, week_offset))
    previous = _radar_metrics(inp, week_bounds(inp.today, week_offset + 1))
    return [{"axis": k, "semana": current[k], "anterior": previous[k]} for k in current]


# ─── Heatmap 90 días ────────────────────────────────────────
def _heat_level(count: int, max_count: int) -> int:
    """0 = nada; 1–4 = intensidad relativa al mejor día del período."""
    if count == 0:
        return 0
    pct = count / max_count
    if pct <= 0.25:
        return 1
    if pct <= 0.5:
        return 2
    if pct <= 0.75:
        return 3
    return 4


def heatmap(inp: StatsInput) -> list[dict[str, Any]]:
    """Celdas por día en columnas de semana (lunes arriba). Las de relleno van con nulls."""
    counts = _daily_habit_counts(inp)
    max_count = max(1, int(counts.max()))
    blank: dict[str, Any] = {"date": None, "count": None, "level": None}

    days = pd.DatetimeIndex(counts.index)
    cells = [blank] * days[0].weekday()
    cells += [
        {"date": day.date(), "count": n, "level": _heat_level(n, max_count)}
        for day, n in zip(days, counts.astype(int).tolist(), strict=True)
    ]
    cells += [blank] * (-len(cells) % 7)
    return cells


# ─── Series y distribución ──────────────────────────────────
def weight_series(inp: StatsInput) -> list[dict[str, Any]]:
    weights = inp.weights.sort_values("date").tail(90)
    return [
        {"date": day, "kg": float(kg)}
        for day, kg in zip(weights["date"].dt.date, weights["kg"].tolist(), strict=True)
    ]


def mood_series(inp: StatsInput) -> list[dict[str, Any]]:
    moods = inp.moods.sort_values("date").tail(30)
    rows = zip(moods["date"].dt.date, moods["mood"].tolist(), moods["sleep"].tolist(), strict=True)
    return [
        {
            "date": day,
            "mood": None if pd.isna(mood) else int(mood),
            "sleep": None if pd.isna(sleep) else float(sleep),
        }
        for day, mood, sleep in rows
    ]


def gym_vs_mma(inp: StatsInput) -> dict[str, int]:
    recent = _between(inp.workouts, inp.today - timedelta(days=30), inp.today)
    counts = recent["kind"].value_counts()
    return {"gym": int(counts.get("gym", 0)), "mma": int(counts.get("mma", 0))}


def _months_back(today: date, months: int) -> date:
    total = today.year * 12 + today.month - 1 - months
    return date(total // 12, total % 12 + 1, 1)


def finance_monthly(inp: StatsInput) -> list[dict[str, Any]]:
    """Ingresos, gastos y % de ahorro de los últimos 6 meses (incluye el actual)."""
    income = inp.income.groupby(inp.income["month"].dt.to_period("M"))["amount"].sum()
    expenses = inp.expenses.groupby(inp.expenses["date"].dt.to_period("M"))["amount"].sum()
    months = []
    for back in range(FINANCE_MONTHS - 1, -1, -1):
        first = _months_back(inp.today, back)
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


def summary(inp: StatsInput, week_offset: int) -> dict[str, Any]:
    week = week_bounds(inp.today, week_offset)
    return {
        "week_start": week.start,
        "week_end": week.end,
        "bruce": bruce_score(inp, week),
        "bruce_history": bruce_history(inp),
        "kpis": kpis(inp),
        "habits_by_week": habits_by_week(inp),
        "radar": radar(inp, week_offset),
        "heatmap": heatmap(inp),
        "weight_series": weight_series(inp),
        "mood_series": mood_series(inp),
        "gym_vs_mma": gym_vs_mma(inp),
        "finance_monthly": finance_monthly(inp),
    }


def earliest_needed(today: date, week_offset: int) -> date:
    """Primer día que necesitan los cálculos (para acotar las consultas)."""
    return min(
        today - timedelta(days=HEATMAP_DAYS - 1),
        week_bounds(today, HISTORY_WEEKS - 1).start,
        week_bounds(today, week_offset + 1).start,
    )
