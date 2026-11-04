from collections.abc import Iterable, Sequence
from datetime import date, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from app.modules.dashboard.schemas.racha_schema import StreakOut
from app.modules.rutina import (
    STREAK_WINDOW_DAYS,
    Habit,
    RoutineBlock,
    block_completions,
    completed_habit_logs,
    day_status,
    list_habits,
    list_routine_blocks,
    streaks,
)


def global_streak(
    today: date,
    blocks: Sequence[RoutineBlock],
    habits: Sequence[Habit],
    done: Iterable[tuple[str, date]],
) -> int:
    """Días seguidos (hacia atrás desde hoy) con al menos el 70 % de la agenda cumplida.

    Los días sin nada agendado no cortan ni suman. Hoy suma si ya llegó al umbral;
    si todavía no, no corta la racha porque el día no terminó.
    """
    days = pd.date_range(end=pd.Timestamp(today), periods=STREAK_WINDOW_DAYS, freq="D")
    return streaks(day_status(today, days, blocks, habits, done))[0]


def get_streak(session: Session, today: date) -> StreakOut:
    start = today - timedelta(days=STREAK_WINDOW_DAYS - 1)
    done = [
        *completed_habit_logs(session, start, today),
        *block_completions(session, start, today),
    ]
    blocks = list_routine_blocks(session)
    habits = list_habits(session, active=True)
    return StreakOut(streak=global_streak(today, blocks, habits, done))
