from datetime import date, datetime, timedelta

from app.modules.dashboard.dashboard_service import global_streak, habit_completion_pct
from app.modules.rutina import Habit, RoutineBlock

MONDAY = date(2026, 10, 12)


def daily_habit() -> Habit:
    return Habit(name="Leer", days_of_week=None)


def test_streak_counts_consecutive_days_over_threshold() -> None:
    today = MONDAY + timedelta(days=4)
    done = [today - timedelta(days=i) for i in range(1, 4)]  # ayer, anteayer, hace 3 días
    assert global_streak(today, [], [daily_habit()], done) == 3


def test_streak_today_counts_once_completed() -> None:
    today = MONDAY
    assert global_streak(today, [], [daily_habit()], [today, today - timedelta(days=1)]) == 2


def test_streak_today_pending_does_not_break() -> None:
    today = MONDAY
    assert global_streak(today, [], [daily_habit()], [today - timedelta(days=1)]) == 1


def test_streak_breaks_under_threshold() -> None:
    today = MONDAY + timedelta(days=3)
    habits = [daily_habit(), Habit(name="Agua", days_of_week=None)]
    # ayer 2/2, anteayer 1/2 (50 %) → corta
    done = [today - timedelta(days=1)] * 2 + [today - timedelta(days=2)]
    assert global_streak(today, [], habits, done) == 1


def test_streak_skips_days_without_agenda() -> None:
    today = MONDAY + timedelta(days=2)  # miércoles
    weekdays_only = Habit(name="Trabajo", days_of_week=[0, 2])  # lunes y miércoles
    assert global_streak(today, [], [weekdays_only], [MONDAY]) == 1


def test_streak_includes_specific_date_blocks() -> None:
    today = MONDAY
    block = RoutineBlock(activity="Médico", repeat_weekly=False, specific_date=today, hour_start=9)
    assert global_streak(today, [block], [], [today]) == 1


def test_new_habit_does_not_break_past_streak() -> None:
    today = MONDAY + timedelta(days=3)
    created_today = Habit(name="Nuevo", days_of_week=None, created_at=datetime(2026, 10, 15, 12))
    new_block = RoutineBlock(
        activity="Correr",
        days_of_week=[0, 1, 2, 3, 4, 5, 6],
        hour_start=7,
        repeat_weekly=True,
        created_at=datetime(2026, 10, 15, 12),
    )
    done = [today - timedelta(days=i) for i in range(1, 4)]
    # Sin la regla de created_at, cada día pasado quedaría en 1/3 y la racha en 0
    assert global_streak(today, [new_block], [daily_habit(), created_today], done) == 3


def test_seventy_percent_is_enough() -> None:
    habits = [Habit(name=str(i), days_of_week=None) for i in range(10)]
    yesterday = MONDAY - timedelta(days=1)
    assert global_streak(MONDAY, [], habits, [yesterday] * 7) == 1  # 7/10 justo


def test_habit_pct_only_counts_until_today() -> None:
    today = MONDAY + timedelta(days=1)  # martes: 2 días esperados
    assert habit_completion_pct(MONDAY, today, [daily_habit()], [MONDAY]) == 50


def test_habit_pct_without_habits_is_none() -> None:
    assert habit_completion_pct(MONDAY, MONDAY, [], []) is None
