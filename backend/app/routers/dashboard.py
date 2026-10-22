from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter
from sqlalchemy import func, select

from app.core.database.conexion_database import SessionDep
from app.models import (
    GymSession,
    Habit,
    HabitLog,
    MmaSession,
    MoodLog,
    RoutineBlock,
    RoutineCompletion,
    WeeklyReview,
)
from app.schemas.rutina import AgendaOut, StreakOut, WeeklyReviewOut, WeeklyReviewSummary
from app.services import dashboard as stats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# `today` lo manda el frontend: es la fecha local del usuario, que el servidor no conoce.


def _completed_habit_dates(session: SessionDep, start: date, end: date) -> list[date]:
    query = (
        select(HabitLog.date)
        .join(Habit)
        .where(Habit.active.is_(True), HabitLog.completed.is_(True))
        .where(HabitLog.date.between(start, end))
    )
    return list(session.scalars(query))


def _attended_days(
    session: SessionDep, model: type[GymSession | MmaSession], start: date, end: date
) -> int:
    query = (
        select(func.count(func.distinct(model.date)))
        .where(model.attended.is_(True))
        .where(model.date.between(start, end))
    )
    return session.scalar(query) or 0


@router.get("/streak", response_model=StreakOut)
def get_streak(today: date, session: SessionDep) -> StreakOut:
    start = today - timedelta(days=stats.STREAK_WINDOW_DAYS - 1)
    habits = list(session.scalars(select(Habit).where(Habit.active.is_(True))))
    blocks = list(session.scalars(select(RoutineBlock)))
    block_dates = session.scalars(
        select(RoutineCompletion.date).where(RoutineCompletion.date.between(start, today))
    )
    done = [*_completed_habit_dates(session, start, today), *block_dates]
    return StreakOut(streak=stats.global_streak(today, blocks, habits, done))


@router.get("/agenda", response_model=AgendaOut)
def get_agenda(date: date, today: date, session: SessionDep) -> dict[str, Any]:
    """Agenda de `date`: secciones con bloques y hábitos ordenados, y el progreso del día."""
    done_blocks = set(
        session.scalars(select(RoutineCompletion.block_id).where(RoutineCompletion.date == date))
    )
    done_habits = set(
        session.scalars(
            select(HabitLog.habit_id).where(HabitLog.date == date, HabitLog.completed.is_(True))
        )
    )
    blocks = list(session.scalars(select(RoutineBlock).order_by(RoutineBlock.hour_start)))
    habits = list(
        session.scalars(
            select(Habit).where(Habit.active.is_(True)).order_by(Habit.sort_order, Habit.created_at)
        )
    )
    return stats.agenda(date, today, blocks, habits, done_blocks, done_habits)


@router.get("/weekly-review", response_model=WeeklyReviewSummary)
def get_weekly_review(today: date, session: SessionDep) -> WeeklyReviewSummary:
    """Cierre de la semana de `today` (lunes a domingo) comparado con la anterior."""
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    prev_start = week_start - timedelta(days=7)
    habits = list(session.scalars(select(Habit).where(Habit.active.is_(True))))
    done = _completed_habit_dates(session, prev_start, week_end)

    habit_pct = stats.habit_completion_pct(week_start, today, habits, done)
    prev_habit_pct = stats.habit_completion_pct(prev_start, today, habits, done)
    avg = session.scalar(
        select(func.avg(MoodLog.mood_score)).where(MoodLog.date.between(week_start, week_end))
    )
    avg_mood = round(float(avg), 2) if avg is not None else None
    review = session.scalar(select(WeeklyReview).where(WeeklyReview.week_start == week_start))
    return WeeklyReviewSummary(
        week_start=week_start,
        week_end=week_end,
        habit_pct=habit_pct,
        prev_habit_pct=prev_habit_pct,
        habit_pct_delta=habit_pct - prev_habit_pct if prev_habit_pct else None,
        gym_days=_attended_days(session, GymSession, week_start, week_end),
        mma_days=_attended_days(session, MmaSession, week_start, week_end),
        avg_mood=avg_mood,
        mood_level=stats.mood_level(avg_mood),
        review=WeeklyReviewOut.model_validate(review) if review else None,
    )
