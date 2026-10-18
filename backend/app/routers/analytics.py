from datetime import date, datetime, time, timedelta
from typing import Any

from fastapi import APIRouter
from sqlalchemy import Select, select

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
    NutritionLog,
    RoutineBlock,
    RoutineCompletion,
    WeightLog,
)
from app.schemas.analytics import AnalyticsData

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _months_back(today: date, months: int) -> date:
    """Primer día del mes, `months` meses antes del actual."""
    total = today.year * 12 + today.month - 1 - months
    return date(total // 12, total % 12 + 1, 1)


@router.get("/data", response_model=AnalyticsData)
def analytics_data(today: date, session: SessionDep) -> AnalyticsData:
    start90 = today - timedelta(days=90)
    start30 = today - timedelta(days=30)
    start6m = _months_back(today, 5)

    def rows(query: Select[Any]) -> list[Any]:
        return list(session.scalars(query))

    return AnalyticsData.model_validate(
        {
            "habits": rows(select(Habit).where(Habit.active.is_(True))),
            "habit_logs": rows(select(HabitLog).where(HabitLog.date >= start90)),
            "routine_blocks": rows(select(RoutineBlock)),
            "routine_completions": rows(
                select(RoutineCompletion).where(RoutineCompletion.date >= start90)
            ),
            "gym": rows(select(GymSession).where(GymSession.date >= start90)),
            "mma": rows(select(MmaSession).where(MmaSession.date >= start90)),
            "weight": rows(select(WeightLog).order_by(WeightLog.date)),
            "mood": rows(select(MoodLog).where(MoodLog.date >= start30).order_by(MoodLog.date)),
            "nutrition": rows(select(NutritionLog).where(NutritionLog.date >= start90)),
            "books": rows(select(Book)),
            "finance_income": rows(select(FinanceIncome).where(FinanceIncome.month >= start6m)),
            "finance_expenses": rows(select(FinanceExpense).where(FinanceExpense.date >= start6m)),
            "journal_entries": rows(
                select(JournalEntry).where(
                    JournalEntry.created_at >= datetime.combine(start90, time.min)
                )
            ),
        },
        from_attributes=True,
    )
