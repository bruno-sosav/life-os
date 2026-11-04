"""Lo que pide el endpoint: lee todo una vez y arma el resumen de la pantalla Stats."""

from datetime import date, timedelta
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.core.fechas_util import week_bounds
from app.modules.analytics.models.estadisticas_model import StatsInput
from app.modules.analytics.repositories import resumen_repository as repository
from app.modules.analytics.schemas.resumen_schema import AnalyticsSummary
from app.modules.analytics.services.cumplimiento_service import (
    HEATMAP_DAYS,
    HISTORY_WEEKS,
    compliance,
    compliance_history,
    heatmap,
)
from app.modules.analytics.services.indicadores_service import habits_by_week, kpis, radar
from app.modules.analytics.services.series_service import (
    FINANCE_MONTHS,
    activity_distribution,
    finance_monthly,
    months_back,
    mood_series,
    weight_series,
)
from app.modules.fisico import attended_days, list_activities
from app.modules.rutina import (
    block_completions,
    completed_habit_logs,
    list_habits,
    list_routine_blocks,
)


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
