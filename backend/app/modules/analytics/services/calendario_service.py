"""Calendario de Stats: el cumplimiento de cada día del mes y de cada semana."""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.fechas_util import days_between, month_bounds, week_bounds
from app.core.numeros_util import js_round
from app.modules.analytics.models.estadisticas_model import StatsInput, day_range, frame, ts
from app.modules.analytics.schemas.calendario_schema import CalendarDay, CalendarMonth, CalendarWeek
from app.modules.analytics.services.cumplimiento_service import done_pairs, week_compliance
from app.modules.rutina import (
    block_completions,
    completed_habit_logs,
    day_status,
    done_per_day,
    expected_per_day,
    list_habits,
    list_routine_blocks,
)


def month_calendar(session: Session, month: date, today: date) -> CalendarMonth:
    period = month_bounds(month)
    # Se leen las semanas enteras: el % de una semana mira también los días de otro mes
    start, end = week_bounds(period.start).start, week_bounds(period.end).end
    inp = StatsInput(
        today=today,
        habits=list_habits(session, active=True),
        blocks=list_routine_blocks(session),
        habit_logs=frame(
            list(completed_habit_logs(session, start, end)), ["habit_id", "date"], ("date",)
        ),
        completions=frame(
            list(block_completions(session, start, end)), ["block_id", "date"], ("date",)
        ),
    )
    days = day_range(period.start, period.end)
    done_list = done_pairs(inp)
    status = day_status(today, days, inp.blocks, inp.habits, done_list)
    status[status.index > ts(today)] = "pendiente"  # todavía no llegó
    expected = expected_per_day(days, inp.blocks, inp.habits)
    done = done_per_day(days, inp.blocks, inp.habits, done_list)

    weeks = []
    monday = start
    while monday <= period.end:
        weeks.append(
            CalendarWeek(week_start=monday, pct=week_compliance(inp, week_bounds(monday))["pct"])
        )
        monday += timedelta(days=7)

    counts = status.value_counts()
    return CalendarMonth(
        days=[
            CalendarDay(
                date=day,
                status=status.iloc[i],
                done=int(done.iloc[i]),
                expected=int(expected.iloc[i]),
                pct=js_round(done.iloc[i] / expected.iloc[i] * 100) if expected.iloc[i] else None,
            )
            for i, day in enumerate(days_between(period))
        ],
        weeks=weeks,
        cumplido=int(counts.get("cumplido", 0)),
        parcial=int(counts.get("parcial", 0)),
        sin_cumplir=int(counts.get("sin_cumplir", 0)),
    )
