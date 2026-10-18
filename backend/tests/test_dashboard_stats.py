from datetime import date, timedelta

from app.models import Habit, RoutineBlock
from app.services.dashboard import global_streak, habit_completion_pct

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


def test_habit_pct_only_counts_until_today() -> None:
    today = MONDAY + timedelta(days=1)  # martes: 2 días esperados
    assert habit_completion_pct(MONDAY, today, [daily_habit()], [MONDAY]) == 50


def test_habit_pct_without_habits_is_zero() -> None:
    assert habit_completion_pct(MONDAY, MONDAY, [], []) == 0
