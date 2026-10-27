"""Rutina: hábitos y sus registros, bloques de horario, completions y cierre semanal."""

from app.modules.rutina.rutina_controller import router
from app.modules.rutina.rutina_model import (
    Habit,
    HabitLog,
    RoutineBlock,
    RoutineCompletion,
    WeeklyReview,
)
from app.modules.rutina.rutina_schema import HabitLogUpsert, LinkedModule
from app.modules.rutina.rutina_service import (
    STREAK_WINDOW_DAYS,
    DayStatus,
    block_completions,
    block_runs_on,
    completed_habit_logs,
    day_status,
    done_per_day,
    expected_per_day,
    get_weekly_review,
    habit_runs_on,
    list_habits,
    list_routine_blocks,
    streaks,
    upsert_habit_log,
)

__all__ = [
    "STREAK_WINDOW_DAYS",
    "DayStatus",
    "Habit",
    "HabitLog",
    "HabitLogUpsert",
    "LinkedModule",
    "RoutineBlock",
    "RoutineCompletion",
    "WeeklyReview",
    "block_completions",
    "block_runs_on",
    "completed_habit_logs",
    "day_status",
    "done_per_day",
    "expected_per_day",
    "get_weekly_review",
    "habit_runs_on",
    "list_habits",
    "list_routine_blocks",
    "router",
    "streaks",
    "upsert_habit_log",
]
