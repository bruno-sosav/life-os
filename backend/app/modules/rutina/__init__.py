"""Rutina: hábitos, bloques de horario, el cierre semanal y las reglas de la racha.

Es lo único que importan los otros módulos.
"""

from fastapi import APIRouter

from app.modules.rutina.controllers import (
    bloques_controller,
    habitos_controller,
    revisiones_controller,
)
from app.modules.rutina.models.bloques_model import RoutineBlock
from app.modules.rutina.models.habitos_model import Habit, HabitLog
from app.modules.rutina.schemas.bloques_schema import RoutineBlockOut
from app.modules.rutina.schemas.habitos_schema import HabitLogUpsert, HabitOut
from app.modules.rutina.schemas.revisiones_schema import WeeklyReviewOut
from app.modules.rutina.services.bloques_service import block_completions, list_routine_blocks
from app.modules.rutina.services.cumplimiento_service import (
    STREAK_WINDOW_DAYS,
    DayStatus,
    block_runs_on,
    day_status,
    done_per_day,
    expected_per_day,
    habit_runs_on,
    scheduled_on,
    streaks,
)
from app.modules.rutina.services.habitos_service import (
    completed_habit_logs,
    list_habits,
    upsert_habit_log,
)
from app.modules.rutina.services.revisiones_service import get_weekly_review

router = APIRouter(tags=["rutina"])
for controller in (habitos_controller, bloques_controller, revisiones_controller):
    router.include_router(controller.router)

__all__ = [
    "STREAK_WINDOW_DAYS",
    "DayStatus",
    "Habit",
    "HabitLog",
    "HabitLogUpsert",
    "HabitOut",
    "RoutineBlock",
    "RoutineBlockOut",
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
    "scheduled_on",
    "streaks",
    "upsert_habit_log",
    "WeeklyReviewOut",
]
