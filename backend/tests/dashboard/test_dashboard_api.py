from collections.abc import Callable

from fastapi.testclient import TestClient


def create_habit(client: TestClient, **fields: object) -> dict[str, object]:
    response = client.post("/api/habits", json={"name": "Leer", **fields})
    assert response.status_code == 201
    data: dict[str, object] = response.json()
    return data


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
