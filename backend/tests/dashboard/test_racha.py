from datetime import datetime, timedelta

from app.modules.dashboard.services.racha_service import global_streak
from app.modules.rutina import Habit, RoutineBlock
from tests.dashboard.ayuda import MONDAY, daily_habit, done


def test_streak_counts_consecutive_days_over_threshold() -> None:
    today = MONDAY + timedelta(days=4)
    days = [today - timedelta(days=i) for i in range(1, 4)]  # ayer, anteayer, hace 3 días
    assert global_streak(today, [], [daily_habit()], done("leer", *days)) == 3


def test_streak_today_counts_once_completed() -> None:
    today = MONDAY
    yesterday = today - timedelta(days=1)
    assert global_streak(today, [], [daily_habit()], done("leer", today, yesterday)) == 2


def test_streak_today_pending_does_not_break() -> None:
    today = MONDAY
    assert global_streak(today, [], [daily_habit()], done("leer", today - timedelta(days=1))) == 1


def test_streak_breaks_under_threshold() -> None:
    today = MONDAY + timedelta(days=3)
    habits = [daily_habit("leer"), daily_habit("agua")]
    yesterday, before = today - timedelta(days=1), today - timedelta(days=2)
    # ayer 2/2, anteayer 1/2 (50 %) → corta
    logs = done("leer", yesterday, before) + done("agua", yesterday)
    assert global_streak(today, [], habits, logs) == 1


def test_streak_skips_days_without_agenda() -> None:
    today = MONDAY + timedelta(days=2)  # miércoles
    weekdays_only = Habit(id="trabajo", name="Trabajo", days_of_week=[0, 2])  # lunes y miércoles
    assert global_streak(today, [], [weekdays_only], done("trabajo", MONDAY)) == 1


def test_streak_includes_specific_date_blocks() -> None:
    today = MONDAY
    block = RoutineBlock(
        id="medico", activity="Médico", repeat_weekly=False, specific_date=today, hour_start=9
    )
    assert global_streak(today, [block], [], done("medico", today)) == 1


def test_new_habit_does_not_break_past_streak() -> None:
    today = MONDAY + timedelta(days=3)
    created_today = daily_habit("nuevo", created_at=datetime(2026, 10, 15, 12))
    new_block = RoutineBlock(
        id="correr",
        activity="Correr",
        days_of_week=[0, 1, 2, 3, 4, 5, 6],
        hour_start=7,
        repeat_weekly=True,
        created_at=datetime(2026, 10, 15, 12),
    )
    days = [today - timedelta(days=i) for i in range(1, 4)]
    # Sin la regla de created_at, cada día pasado quedaría en 1/3 y la racha en 0
    assert (
        global_streak(today, [new_block], [daily_habit(), created_today], done("leer", *days)) == 3
    )


def test_unscheduled_done_does_not_count() -> None:
    """Gym es solo lunes: marcarlo el martes no tapa el bloque que faltó ese día."""
    today = MONDAY + timedelta(days=2)
    tuesday = MONDAY + timedelta(days=1)
    gym = Habit(id="gym", name="Gym", days_of_week=[0])
    blocks = [
        RoutineBlock(
            id=f"b{i}", activity=str(i), days_of_week=[1], hour_start=9, repeat_weekly=True
        )
        for i in range(2)
    ]
    # martes: 1 de 2 bloques + gym (no tocaba) → 50 %, no cumple
    logs = done("gym", MONDAY, tuesday) + done("b0", tuesday)
    assert global_streak(today, blocks, [gym], logs) == 0


def test_seventy_percent_is_enough() -> None:
    habits = [daily_habit(str(i)) for i in range(10)]
    yesterday = MONDAY - timedelta(days=1)
    logs = [(str(i), yesterday) for i in range(7)]
    assert global_streak(MONDAY, [], habits, logs) == 1  # 7/10 justo
