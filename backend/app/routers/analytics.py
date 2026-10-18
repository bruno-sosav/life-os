from datetime import date, timedelta
from typing import Annotated, Any

import pandas as pd
from fastapi import APIRouter, Query
from sqlalchemy import select

from app.db import SessionDep
from app.models import (
    Book,
    FinanceExpense,
    FinanceIncome,
    GymSession,
    Habit,
    HabitLog,
    JournalEntry,
    MmaSession,
    MoodLog,
    RoutineBlock,
    RoutineCompletion,
    WeightLog,
)
from app.schemas.analytics import AnalyticsSummary
from app.services import analytics as stats

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _frame(rows: list[tuple[Any, ...]], columns: list[str], dates: tuple[str, ...]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=columns)
    for column in dates:
        df[column] = pd.to_datetime(df[column])
    return df


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(
    today: date, session: SessionDep, week_offset: Annotated[int, Query(ge=0, le=520)] = 0
) -> AnalyticsSummary:
    """Todo lo de la pantalla Stats, calculado. `week_offset` mueve la semana del Score/radar."""
    start = stats.earliest_needed(today, week_offset)
    finance_start = stats.months_back(today, stats.FINANCE_MONTHS - 1)

    habits = list(session.scalars(select(Habit).where(Habit.active.is_(True))))
    habit_logs = session.execute(
        select(HabitLog.habit_id, HabitLog.date)
        .join(Habit)
        .where(Habit.active.is_(True), HabitLog.completed.is_(True))
        .where(HabitLog.date.between(start, today))
    ).all()
    completions = session.execute(
        select(RoutineCompletion.block_id, RoutineCompletion.date).where(
            RoutineCompletion.date.between(start, today)
        )
    ).all()
    workouts = [
        ("gym", day)
        for day in session.scalars(
            select(GymSession.date).where(GymSession.attended.is_(True), GymSession.date >= start)
        )
    ] + [
        ("mma", day)
        for day in session.scalars(
            select(MmaSession.date).where(MmaSession.attended.is_(True), MmaSession.date >= start)
        )
    ]
    moods = session.execute(
        select(MoodLog.date, MoodLog.mood_score, MoodLog.sleep_hours).where(
            MoodLog.date.between(min(start, today - timedelta(days=30)), today)
        )
    ).all()

    inp = stats.StatsInput(
        today=today,
        habits=habits,
        blocks=list(session.scalars(select(RoutineBlock))),
        habit_logs=_frame(list(habit_logs), ["habit_id", "date"], ("date",)),
        completions=_frame(list(completions), ["block_id", "date"], ("date",)),
        workouts=_frame(workouts, ["kind", "date"], ("date",)),
        weights=_frame(
            list(session.execute(select(WeightLog.date, WeightLog.weight_kg)).all()),
            ["date", "kg"],
            ("date",),
        ),
        moods=_frame(list(moods), ["date", "mood", "sleep"], ("date",)),
        journal=_frame(
            [
                (d,)
                for d in session.scalars(
                    select(JournalEntry.date).where(JournalEntry.date >= start)
                )
            ],
            ["date"],
            ("date",),
        ),
        books_finished=[
            d
            for d in session.scalars(
                select(Book.finished_at).where(
                    Book.status == "leido", Book.finished_at.is_not(None)
                )
            )
            if d is not None
        ],
        income=_frame(
            list(
                session.execute(
                    select(FinanceIncome.month, FinanceIncome.amount).where(
                        FinanceIncome.month >= min(start, finance_start)
                    )
                ).all()
            ),
            ["month", "amount"],
            ("month",),
        ),
        expenses=_frame(
            list(
                session.execute(
                    select(FinanceExpense.date, FinanceExpense.amount).where(
                        FinanceExpense.date >= min(start, finance_start)
                    )
                ).all()
            ),
            ["date", "amount"],
            ("date",),
        ),
    )
    return AnalyticsSummary.model_validate(stats.summary(inp, week_offset))
