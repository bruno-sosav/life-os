from collections.abc import Callable
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.modules.dashboard.services.cierre_service import habit_completion_pct, mood_level
from tests.dashboard.ayuda import MONDAY, create_habit, daily_habit, done


def test_habit_pct_only_counts_until_today() -> None:
    today = MONDAY + timedelta(days=1)  # martes: 2 días esperados
    assert habit_completion_pct(MONDAY, today, [daily_habit()], done("leer", MONDAY)) == 50


@pytest.mark.parametrize(
    ("avg", "level"),
    [
        (None, None),
        (4.5, "excelente"),
        (4.4, "buena"),
        (3.5, "buena"),
        (2.5, "regular"),
        (2.4, "dificil"),
    ],
)
def test_mood_level_cuts(avg: float | None, level: str | None) -> None:
    assert mood_level(avg) == level


def test_habit_pct_without_habits_is_none() -> None:
    assert habit_completion_pct(MONDAY, MONDAY, [], []) is None


def test_streak_and_weekly_stats_endpoints(
    client: TestClient, backdate_habits: Callable[[], None]
) -> None:
    habit = create_habit(client)
    backdate_habits()
    for day in ("2026-10-12", "2026-10-13"):
        client.put(
            "/api/habit-logs", json={"habit_id": habit["id"], "date": day, "completed": True}
        )

    streak = client.get("/api/dashboard/streak", params={"today": "2026-10-13"}).json()
    assert streak == {"streak": 2}

    weekly = client.get("/api/dashboard/weekly-review", params={"today": "2026-10-14"}).json()
    assert weekly == {
        "week_start": "2026-10-12",
        "week_end": "2026-10-18",
        "habit_pct": 67,
        "prev_habit_pct": 0,
        "habit_pct_delta": 67,  # la semana anterior tocaba el hábito y quedó en 0 %
        "activity_days": [],
        "avg_mood": None,
        "mood_level": None,
        "review": None,
    }

    client.put("/api/weekly-reviews/2026-10-12", json={"went_well": "Constancia"})
    weekly = client.get("/api/dashboard/weekly-review", params={"today": "2026-10-18"}).json()
    assert weekly["review"]["went_well"] == "Constancia"


def test_weekly_review_days_per_activity(client: TestClient) -> None:
    def activity(name: str, active: bool = True) -> str:
        body = {"name": name, "active": active}
        return str(client.post("/api/activities", json=body).json()["id"])

    gym, mma, swim = activity("Gym"), activity("MMA", active=False), activity("Natación", False)
    for day in ("2026-10-12", "2026-10-12", "2026-10-14"):  # dos sesiones el mismo día
        client.post("/api/sessions", json={"activity_id": gym, "date": day})
    client.post("/api/sessions", json={"activity_id": mma, "date": "2026-10-13"})
    client.post("/api/sessions", json={"activity_id": swim, "date": "2026-10-01"})  # otra semana

    weekly = client.get("/api/dashboard/weekly-review", params={"today": "2026-10-14"}).json()
    # La pausada aparece solo si igual se usó esa semana
    assert [(a["name"], a["days"]) for a in weekly["activity_days"]] == [("Gym", 2), ("MMA", 1)]


def test_linked_habit_counts_as_a_training_day(client: TestClient) -> None:
    habit = create_habit(client, name="Ir al gym")
    gym = client.post("/api/activities", json={"name": "Gym", "habit_id": habit["id"]}).json()
    # Marcado desde el dashboard y con sesión el mismo día
    client.put(
        "/api/habit-logs", json={"habit_id": habit["id"], "date": "2026-10-13", "completed": True}
    )
    client.post("/api/sessions", json={"activity_id": gym["id"], "date": "2026-10-13"})
    client.post("/api/sessions", json={"activity_id": gym["id"], "date": "2026-10-14"})

    weekly = client.get("/api/dashboard/weekly-review", params={"today": "2026-10-14"}).json()
    assert weekly["activity_days"][0]["days"] == 2  # el 13 cuenta una sola vez
    summary = client.get("/api/analytics/summary", params={"today": "2026-10-14"}).json()
    assert summary["activity_distribution"][0]["count"] == 2
