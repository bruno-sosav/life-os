from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.rutina import HabitLog
from tests.rutina.ayuda import MONDAY, agenda, agenda_done, create_habit


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


def test_list_habits_by_time_and_active(client: TestClient) -> None:
    create_habit(client, name="Sin hora")
    create_habit(client, name="Tarde", start_time="18:00")
    create_habit(client, name="Mañana", start_time="07:00")
    paused = create_habit(client, name="Pausado")
    client.patch(f"/api/habits/{paused['id']}", json={"active": False})

    names = [h["name"] for h in client.get("/api/habits", params={"active": True}).json()]
    assert names == ["Mañana", "Tarde", "Sin hora"]
    assert len(client.get("/api/habits").json()) == 4


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


def test_habit_days_normalized(client: TestClient) -> None:
    assert create_habit(client, days_of_week=[0, 1, 2, 3, 4, 5, 6])["days_of_week"] is None
    assert create_habit(client, days_of_week=[])["days_of_week"] is None
    assert create_habit(client, days_of_week=[4, 0, 4])["days_of_week"] == [0, 4]
