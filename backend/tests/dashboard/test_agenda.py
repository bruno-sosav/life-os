from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.modules.dashboard.services.agenda_service import agenda
from tests.dashboard.ayuda import MONDAY, create_habit, daily_habit


def test_past_agenda_hides_what_did_not_exist_yet() -> None:
    created_today = daily_habit("nuevo", created_at=datetime(2026, 10, 13, 12))
    old = daily_habit("leer")
    yesterday = agenda(MONDAY, MONDAY + timedelta(days=1), [], [old, created_today], set(), set())
    today = agenda(
        MONDAY + timedelta(days=1),
        MONDAY + timedelta(days=1),
        [],
        [old, created_today],
        set(),
        set(),
    )
    assert (yesterday["total"], today["total"]) == (1, 2)


def test_agenda(client: TestClient) -> None:
    # Lunes 2026-10-19
    block = {"hour_start": 7, "hour_min": 30, "hour_end": 8, "activity": "Gym", "days_of_week": [0]}
    gym = client.post("/api/routine-blocks", json=block).json()
    client.post("/api/routine-blocks", json={**block, "activity": "Martes", "days_of_week": [1]})
    late = {**block, "hour_start": 21, "activity": "Leer", "repeat_weekly": False}
    client.post("/api/routine-blocks", json={**late, "specific_date": "2026-10-19"})
    water = create_habit(client, name="Agua")
    create_habit(client, name="Meditar", start_time="13:05")
    create_habit(client, name="Finde", days_of_week=[5, 6])

    client.put(
        "/api/routine-completions",
        json={"block_id": gym["id"], "date": "2026-10-19", "completed": True},
    )
    client.put(
        "/api/habit-logs", json={"habit_id": water["id"], "date": "2026-10-19", "completed": True}
    )

    agenda = client.get(
        "/api/dashboard/agenda", params={"date": "2026-10-19", "today": "2026-10-19"}
    ).json()
    sections = {
        s["key"]: [(i["title"], i["time"], i["done"]) for i in s["items"]]
        for s in agenda["sections"]
    }
    assert sections == {
        "manana": [("Gym", "07:30", True)],
        "tarde": [("Meditar", "13:05", False)],
        "noche": [("Leer", "21:30", False)],
        "sin_horario": [("Agua", None, True)],
    }
    assert (agenda["completed"], agenda["total"], agenda["pct"]) == (2, 4, 50)
    assert agenda["weekday"] == 0
    assert [d["is_today"] for d in agenda["week"]] == [True, *[False] * 6]
    assert agenda["sections"][0]["items"][0]["block"]["id"] == gym["id"]

    # Jueves: solo los hábitos diarios, ninguno hecho
    thursday = client.get(
        "/api/dashboard/agenda", params={"date": "2026-10-22", "today": "2026-10-22"}
    ).json()
    assert [i["title"] for s in thursday["sections"] for i in s["items"]] == ["Meditar", "Agua"]
    assert (thursday["completed"], thursday["total"], thursday["pct"]) == (0, 2, 0)
