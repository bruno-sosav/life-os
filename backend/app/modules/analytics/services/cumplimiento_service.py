"""Cumplimiento: % de lo agendado por semana y estado de cada día."""

from collections.abc import Sequence
from datetime import date, timedelta
from typing import Any

import pandas as pd

from app.core.fechas_util import Period, week_bounds
from app.core.numeros_util import js_round
from app.modules.analytics.models.estadisticas_model import StatsInput, day_range
from app.modules.rutina import STREAK_WINDOW_DAYS, Habit, day_status, done_per_day, expected_per_day

HISTORY_WEEKS = 12


def expected_habits(habits: Sequence[Habit], start: date, end: date) -> int:
    return int(expected_per_day(day_range(start, end), [], habits).sum())


def done_habits(inp: StatsInput, start: date, end: date) -> int:
    """Hábitos cumplidos en el rango, contando solo los días en que tocaban."""
    return int(done_per_day(day_range(start, end), [], inp.habits, done_pairs(inp)).sum())


def week_compliance(inp: StatsInput, week: Period) -> dict[str, Any]:
    """% de lo agendado (hábitos y bloques) que se hizo en la semana, contando hasta hoy.

    Cada día suma solo lo que tenía agendado: hacer algo extra no tapa lo que faltó.
    pct es None si en la semana no había nada agendado.
    """
    end = min(week.end, inp.today)
    if end < week.start:
        return {"pct": None, "done": 0, "expected": 0}
    days = day_range(week.start, end)
    expected = expected_per_day(days, inp.blocks, inp.habits)
    done = done_per_day(days, inp.blocks, inp.habits, done_pairs(inp))
    total, did = int(expected.sum()), int(done.sum())
    return {"pct": js_round(did / total * 100) if total else None, "done": did, "expected": total}


def compliance(inp: StatsInput, week_offset: int) -> dict[str, Any]:
    current = week_compliance(inp, week_bounds(inp.today, week_offset))
    previous = week_compliance(inp, week_bounds(inp.today, week_offset + 1))["pct"]
    both = current["pct"] is not None and previous is not None
    return {**current, "prev_pct": previous, "delta": current["pct"] - previous if both else None}


def compliance_history(inp: StatsInput) -> list[dict[str, Any]]:
    return [
        {
            "week_start": week.start,
            "pct": week_compliance(inp, week)["pct"],
            "is_current": offset == 0,
        }
        for offset in range(HISTORY_WEEKS - 1, -1, -1)
        for week in [week_bounds(inp.today, offset)]
    ]


def done_pairs(inp: StatsInput) -> list[tuple[str, date]]:
    """(id, fecha) de cada hábito o bloque cumplido."""
    habits = zip(inp.habit_logs["habit_id"], inp.habit_logs["date"].dt.date, strict=True)
    blocks = zip(inp.completions["block_id"], inp.completions["date"].dt.date, strict=True)
    return [*habits, *blocks]


def daily_status(inp: StatsInput) -> pd.Series:
    """Estado de cada uno de los últimos 90 días, contando hábitos y bloques de rutina."""
    days = day_range(inp.today - timedelta(days=STREAK_WINDOW_DAYS - 1), inp.today)
    return day_status(inp.today, days, inp.blocks, inp.habits, done_pairs(inp))
