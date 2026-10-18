from datetime import date, timedelta

from fastapi import APIRouter
from sqlalchemy import func, select

from app.db import SessionDep
from app.models import (
    GymSession,
    Habit,
    HabitLog,
    MmaSession,
    MoodLog,
    RoutineBlock,
    RoutineCompletion,
)
from app.schemas.rutina import StreakOut, WeeklyStatsOut
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


@router.get("/weekly-stats", response_model=WeeklyStatsOut)
def get_weekly_stats(week_start: date, today: date, session: SessionDep) -> WeeklyStatsOut:
    week_end = week_start + timedelta(days=6)
    prev_start = week_start - timedelta(days=7)
    habits = list(session.scalars(select(Habit).where(Habit.active.is_(True))))
    done = _completed_habit_dates(session, prev_start, week_end)

    avg_mood = session.scalar(
        select(func.avg(MoodLog.mood_score)).where(MoodLog.date.between(week_start, week_end))
    )
    return WeeklyStatsOut(
        habit_pct=stats.habit_completion_pct(week_start, today, habits, done),
        prev_habit_pct=stats.habit_completion_pct(prev_start, today, habits, done),
        gym_days=_attended_days(session, GymSession, week_start, week_end),
        mma_days=_attended_days(session, MmaSession, week_start, week_end),
        avg_mood=round(float(avg_mood), 2) if avg_mood is not None else None,
    )
