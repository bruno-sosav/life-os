"""Helpers compartidos por los tests del Dashboard."""

from datetime import date

from fastapi.testclient import TestClient

from app.modules.rutina import Habit

MONDAY = date(2026, 10, 12)


def daily_habit(habit_id: str = "leer", **fields: object) -> Habit:
    return Habit(id=habit_id, name=habit_id, days_of_week=None, **fields)


def done(item_id: str, *days: date) -> list[tuple[str, date]]:
    return [(item_id, day) for day in days]


def create_habit(client: TestClient, **fields: object) -> dict[str, object]:
    response = client.post("/api/habits", json={"name": "Leer", **fields})
    assert response.status_code == 201
    data: dict[str, object] = response.json()
    return data
