"""Estadísticas de la pantalla Stats: cumplimiento semanal, KPIs, radar, heatmap y series.

Las funciones son puras: reciben los registros ya leídos de la base (en DataFrames con
una columna `date` de tipo datetime64) y devuelven estructuras listas para serializar.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.core.fechas_util import Period, week_bounds
from app.core.numeros_util import js_round
from app.modules.analytics import analytics_repository as repository
from app.modules.analytics.analytics_schema import AnalyticsSummary
from app.modules.fisico import Activity, attended_days, list_activities
from app.modules.rutina import (
    STREAK_WINDOW_DAYS,
    Habit,
    RoutineBlock,
    block_completions,
    completed_habit_logs,
    day_status,
    done_per_day,
    expected_per_day,
    list_habits,
    list_routine_blocks,
    streaks,
)

WORKOUT_GOAL = 5  # días de entreno por semana que llenan el eje del radar
HEATMAP_DAYS = STREAK_WINDOW_DAYS
HISTORY_WEEKS = 12
HABIT_WEEKS = 8
FINANCE_MONTHS = 6


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
    # Todas las actividades (también las pausadas: sus sesiones viejas siguen contando)
    activities: Sequence[Activity] = ()
    # Días con cada actividad (sesión asistida o hábito vinculado cumplido): activity_id, date
    workouts: pd.DataFrame = field(default_factory=lambda: _empty("activity_id", "date"))
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


# ─── Cumplimiento semanal ───────────────────────────────────
def week_compliance(inp: StatsInput, week: Period) -> dict[str, Any]:
    """% de lo agendado (hábitos y bloques) que se hizo en la semana, contando hasta hoy.

    Cada día suma como mucho lo que tenía agendado: hacer algo extra no tapa lo que faltó.
    pct es None si en la semana no había nada agendado.
    """
    end = min(week.end, inp.today)
    if end < week.start:
        return {"pct": None, "done": 0, "expected": 0}
    days = _days(week.start, end)
    expected = expected_per_day(days, inp.blocks, inp.habits)
    done = done_per_day(days, _done_dates(inp)).clip(upper=expected)
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


# ─── Cumplimiento diario (misma regla del 70 % que la racha del dashboard) ──
def _done_dates(inp: StatsInput) -> list[date]:
    """Una fecha por cada hábito o bloque cumplido."""
    return list(pd.concat([inp.habit_logs["date"], inp.completions["date"]]).dt.date)


def daily_status(inp: StatsInput) -> pd.Series:
    """Estado de cada uno de los últimos 90 días, contando hábitos y bloques de rutina."""
    days = _days(inp.today - timedelta(days=HEATMAP_DAYS - 1), inp.today)
    return day_status(inp.today, days, inp.blocks, inp.habits, _done_dates(inp))


# ─── KPIs ───────────────────────────────────────────────────
def kpis(inp: StatsInput) -> dict[str, Any]:
    today = inp.today
    month_start = today.replace(day=1)
    current_streak, best_streak = streaks(daily_status(inp))

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
def _radar_metrics(inp: StatsInput, week: Period) -> dict[str, int]:
    expected = _expected_habits(inp.habits, week.start, week.end)
    done = len(_between(inp.habit_logs, week.start, week.end))
    workouts = len(_between(inp.workouts, week.start, week.end))
    mental_dates = pd.concat(
        [
            _between(inp.journal, week.start, week.end)["date"],
            _between(inp.moods, week.start, week.end)["date"],
        ]
    ).nunique()
    return {
        "Hábitos": js_round(done / expected * 100) if expected else 0,
        "Entrenos": js_round(min(workouts / WORKOUT_GOAL, 1) * 100),
        "Mental": js_round(min(mental_dates / 7, 1) * 100),
    }


def radar(inp: StatsInput, week_offset: int) -> list[dict[str, Any]]:
    current = _radar_metrics(inp, week_bounds(inp.today, week_offset))
    previous = _radar_metrics(inp, week_bounds(inp.today, week_offset + 1))
    return [{"axis": k, "semana": current[k], "anterior": previous[k]} for k in current]


# ─── Heatmap 90 días ────────────────────────────────────────
def heatmap(inp: StatsInput) -> dict[str, Any]:
    """Celdas por día en columnas de semana (lunes arriba) y cuántos días hubo de cada estado.

    Las celdas de relleno van con nulls.
    """
    status = daily_status(inp)
    blank: dict[str, Any] = {"date": None, "status": None}
    days = pd.DatetimeIndex(status.index)
    cells = [blank] * days[0].weekday()
    cells += [{"date": day.date(), "status": s} for day, s in zip(days, status, strict=True)]
    cells += [blank] * (-len(cells) % 7)
    counts = status.value_counts()
    return {
        "cells": cells,
        "cumplido": int(counts.get("cumplido", 0)),
        "parcial": int(counts.get("parcial", 0)),
        "sin_cumplir": int(counts.get("sin_cumplir", 0)),
    }


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


def activity_distribution(inp: StatsInput) -> list[dict[str, Any]]:
    """Días de cada actividad en los últimos 30 días, de la más hecha a la menos."""
    recent = _between(inp.workouts, inp.today - timedelta(days=30), inp.today)
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


def summary(inp: StatsInput, week_offset: int) -> dict[str, Any]:
    week = week_bounds(inp.today, week_offset)
    return {
        "week_start": week.start,
        "week_end": week.end,
        "compliance": compliance(inp, week_offset),
        "compliance_history": compliance_history(inp),
        "kpis": kpis(inp),
        "habits_by_week": habits_by_week(inp),
        "radar": radar(inp, week_offset),
        "heatmap": heatmap(inp),
        "weight_series": weight_series(inp),
        "mood_series": mood_series(inp),
        "activity_distribution": activity_distribution(inp),
        "finance_monthly": finance_monthly(inp),
    }


def earliest_needed(today: date, week_offset: int) -> date:
    """Primer día que necesitan los cálculos (para acotar las consultas)."""
    return min(
        today - timedelta(days=HEATMAP_DAYS - 1),
        week_bounds(today, HISTORY_WEEKS - 1).start,
        week_bounds(today, week_offset + 1).start,
    )


# ─── Lo que pide el endpoint ────────────────────────────────
def _frame(rows: list[tuple[Any, ...]], columns: list[str], dates: tuple[str, ...]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=columns)
    for column in dates:
        df[column] = pd.to_datetime(df[column])
    return df


def get_summary(session: Session, today: date, week_offset: int) -> AnalyticsSummary:
    start = earliest_needed(today, week_offset)
    finance_start = min(start, months_back(today, FINANCE_MONTHS - 1))
    mood_start = min(start, today - timedelta(days=30))

    inp = StatsInput(
        today=today,
        habits=list_habits(session, active=True),
        blocks=list_routine_blocks(session),
        habit_logs=_frame(
            list(completed_habit_logs(session, start, today)), ["habit_id", "date"], ("date",)
        ),
        completions=_frame(
            list(block_completions(session, start, today)), ["block_id", "date"], ("date",)
        ),
        activities=list_activities(session),
        workouts=_frame(
            list(attended_days(session, start, today)), ["activity_id", "date"], ("date",)
        ),
        weights=_frame(repository.weights(session), ["date", "kg"], ("date",)),
        moods=_frame(
            repository.moods(session, mood_start, today), ["date", "mood", "sleep"], ("date",)
        ),
        journal=_frame(
            [(d,) for d in repository.journal_dates(session, start)], ["date"], ("date",)
        ),
        books_finished=repository.finished_book_dates(session),
        income=_frame(repository.income(session, finance_start), ["month", "amount"], ("month",)),
        expenses=_frame(repository.expenses(session, finance_start), ["date", "amount"], ("date",)),
    )
    return AnalyticsSummary.model_validate(summary(inp, week_offset))
