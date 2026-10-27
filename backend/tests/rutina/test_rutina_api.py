from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.rutina import HabitLog

MONDAY = "2026-10-12"


def create_habit(client: TestClient, **fields: object) -> dict[str, object]:
    response = client.post("/api/habits", json={"name": "Leer", **fields})
    assert response.status_code == 201
    data: dict[str, object] = response.json()
    return data


def agenda(client: TestClient, day: str = MONDAY) -> dict[str, Any]:
    data: dict[str, Any] = client.get(
        "/api/dashboard/agenda", params={"date": day, "today": day}
    ).json()
    return data


def agenda_done(client: TestClient, item_id: object) -> bool:
    items = [it for section in agenda(client)["sections"] for it in section["items"]]
    return next(bool(it["done"]) for it in items if it["id"] == item_id)


def test_habit_crud(client: TestClient) -> None:
    habit = create_habit(client, emoji="📚", days_of_week=[0, 2], start_time="08:30")
    assert habit["active"] is True
    assert habit["start_time"] == "08:30:00"

    response = client.patch(f"/api/habits/{habit['id']}", json={"name": "Leer 20 min"})
    assert response.json()["name"] == "Leer 20 min"
    assert response.json()["days_of_week"] == [0, 2]

    assert agenda(client)["total"] == 1  # lunes: le toca
    assert client.delete(f"/api/habits/{habit['id']}").status_code == 204
    assert agenda(client)["total"] == 0


def test_habit_validation(client: TestClient) -> None:
    assert client.post("/api/habits", json={"name": "X", "days_of_week": [7]}).status_code == 422
    assert client.post("/api/habits", json={"name": ""}).status_code == 422
    assert client.patch("/api/habits/no-existe", json={"name": "X"}).status_code == 404


def test_habit_log_upsert_and_cascade(client: TestClient, db: sessionmaker[Session]) -> None:
    habit = create_habit(client)
    log = {"habit_id": habit["id"], "date": MONDAY, "completed": True}
    assert client.put("/api/habit-logs", json=log).json()["completed"] is True
    assert agenda_done(client, habit["id"]) is True
    client.put("/api/habit-logs", json={**log, "completed": False})
    assert agenda_done(client, habit["id"]) is False

    client.delete(f"/api/habits/{habit['id']}")
    with db() as session:
        assert session.scalar(select(func.count(HabitLog.id))) == 0


def test_routine_blocks_and_completions(client: TestClient) -> None:
    block = {"days_of_week": [0, 3], "hour_start": 7, "hour_end": 8, "activity": "Gym"}
    created = client.post("/api/routine-blocks", json=block).json()

    updated = client.put(f"/api/routine-blocks/{created['id']}", json={**block, "hour_end": 9})
    assert updated.json()["hour_end"] == 9

    toggle = {"block_id": created["id"], "date": MONDAY, "completed": True}
    assert client.put("/api/routine-completions", json=toggle).status_code == 204
    client.put("/api/routine-completions", json=toggle)  # idempotente
    assert agenda_done(client, created["id"]) is True
    assert agenda(client)["completed"] == 1

    client.put("/api/routine-completions", json={**toggle, "completed": False})
    assert agenda_done(client, created["id"]) is False


def test_weekly_review_upsert(client: TestClient) -> None:
    def review() -> Any:
        params = {"today": "2026-10-14"}
        return client.get("/api/dashboard/weekly-review", params=params).json()["review"]

    assert review() is None
    client.put(f"/api/weekly-reviews/{MONDAY}", json={"went_well": "Gym 4 veces"})
    client.put(f"/api/weekly-reviews/{MONDAY}", json={"went_well": "Gym 5 veces"})
    assert review()["went_well"] == "Gym 5 veces"


def test_habit_days_normalized(client: TestClient) -> None:
    assert create_habit(client, days_of_week=[0, 1, 2, 3, 4, 5, 6])["days_of_week"] is None
    assert create_habit(client, days_of_week=[])["days_of_week"] is None
    assert create_habit(client, days_of_week=[4, 0, 4])["days_of_week"] == [0, 4]


def test_routine_block_schedule_rules(client: TestClient) -> None:
    base = {"hour_start": 7, "hour_end": 8, "activity": "Gym"}
    multi = client.post("/api/routine-blocks", json={**base, "days_of_week": [3, 1, 3]}).json()
    assert multi["days_of_week"] == [1, 3]

    one_off = {**base, "repeat_weekly": False, "specific_date": "2026-10-20", "days_of_week": [1]}
    created = client.post("/api/routine-blocks", json=one_off).json()
    assert (created["days_of_week"], created["specific_date"]) == (None, "2026-10-20")

    assert client.post("/api/routine-blocks", json={**base, "days_of_week": []}).status_code == 422
    no_date = {**base, "repeat_weekly": False}
    assert client.post("/api/routine-blocks", json=no_date).status_code == 422
