from fastapi.testclient import TestClient


def create_habit(client: TestClient, **fields: object) -> dict[str, object]:
    response = client.post("/api/habits", json={"name": "Leer", **fields})
    assert response.status_code == 201
    data: dict[str, object] = response.json()
    return data


def test_habit_crud(client: TestClient) -> None:
    habit = create_habit(client, emoji="📚", days_of_week=[0, 2], start_time="08:30")
    assert habit["active"] is True
    assert habit["start_time"] == "08:30:00"

    response = client.patch(f"/api/habits/{habit['id']}", json={"name": "Leer 20 min"})
    assert response.json()["name"] == "Leer 20 min"
    assert response.json()["days_of_week"] == [0, 2]

    assert client.delete(f"/api/habits/{habit['id']}").status_code == 204
    assert client.get("/api/habits").json() == []


def test_habits_order_and_filters(client: TestClient) -> None:
    create_habit(client, name="Sin hora")
    create_habit(client, name="Tarde", start_time="18:00")
    create_habit(client, name="Mañana", start_time="07:00", linked_module="gym")

    names = [h["name"] for h in client.get("/api/habits", params={"active": True}).json()]
    assert names == ["Mañana", "Tarde", "Sin hora"]

    gym = client.get("/api/habits", params={"linked_module": "gym"}).json()
    assert [h["name"] for h in gym] == ["Mañana"]


def test_habit_validation(client: TestClient) -> None:
    assert client.post("/api/habits", json={"name": "X", "days_of_week": [7]}).status_code == 422
    assert client.post("/api/habits", json={"name": ""}).status_code == 422
    assert client.patch("/api/habits/no-existe", json={"name": "X"}).status_code == 404


def test_habit_log_upsert_and_cascade(client: TestClient) -> None:
    habit = create_habit(client)
    log = {"habit_id": habit["id"], "date": "2026-10-12", "completed": True}
    client.put("/api/habit-logs", json=log)
    client.put("/api/habit-logs", json={**log, "completed": False})

    logs = client.get("/api/habit-logs", params={"start": "2026-10-12", "end": "2026-10-18"})
    assert [entry["completed"] for entry in logs.json()] == [False]

    client.delete(f"/api/habits/{habit['id']}")
    logs = client.get("/api/habit-logs", params={"start": "2026-10-12", "end": "2026-10-18"})
    assert logs.json() == []


def test_routine_blocks_and_completions(client: TestClient) -> None:
    block = {"days_of_week": [0, 3], "hour_start": 7, "hour_end": 8, "activity": "Gym"}
    created = client.post("/api/routine-blocks", json=block).json()

    updated = client.put(f"/api/routine-blocks/{created['id']}", json={**block, "hour_end": 9})
    assert updated.json()["hour_end"] == 9

    toggle = {"block_id": created["id"], "date": "2026-10-12", "completed": True}
    assert client.put("/api/routine-completions", json=toggle).status_code == 204
    client.put("/api/routine-completions", json=toggle)  # idempotente
    day = client.get("/api/routine-completions", params={"date": "2026-10-12"}).json()
    assert len(day) == 1

    client.put("/api/routine-completions", json={**toggle, "completed": False})
    assert client.get("/api/routine-completions", params={"date": "2026-10-12"}).json() == []


def test_weekly_review_upsert(client: TestClient) -> None:
    assert client.get("/api/weekly-reviews/2026-10-12").json() is None
    client.put("/api/weekly-reviews/2026-10-12", json={"went_well": "Gym 4 veces"})
    client.put("/api/weekly-reviews/2026-10-12", json={"went_well": "Gym 5 veces"})
    review = client.get("/api/weekly-reviews/2026-10-12").json()
    assert review["went_well"] == "Gym 5 veces"


def test_streak_and_weekly_stats_endpoints(client: TestClient) -> None:
    habit = create_habit(client)
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
        "habit_pct_delta": None,
        "gym_days": 0,
        "mma_days": 0,
        "avg_mood": None,
        "mood_level": None,
        "review": None,
    }

    client.put("/api/weekly-reviews/2026-10-12", json={"went_well": "Constancia"})
    weekly = client.get("/api/dashboard/weekly-review", params={"today": "2026-10-18"}).json()
    assert weekly["review"]["went_well"] == "Constancia"


def test_habit_days_normalized(client: TestClient) -> None:
    assert create_habit(client, days_of_week=[0, 1, 2, 3, 4, 5, 6])["days_of_week"] is None
    assert create_habit(client, days_of_week=[])["days_of_week"] is None
    assert create_habit(client, days_of_week=[4, 0, 4])["days_of_week"] == [0, 4]


def test_routine_block_schedule_rules(client: TestClient) -> None:
    base = {"hour_start": 7, "hour_end": 8, "activity": "Gym"}
    single = client.post("/api/routine-blocks", json={**base, "days_of_week": [2]}).json()
    assert (single["days_of_week"], single["day_of_week"]) == ([2], 2)

    multi = client.post("/api/routine-blocks", json={**base, "days_of_week": [3, 1]}).json()
    assert (multi["days_of_week"], multi["day_of_week"]) == ([1, 3], None)

    one_off = {**base, "repeat_weekly": False, "specific_date": "2026-10-20", "days_of_week": [1]}
    created = client.post("/api/routine-blocks", json=one_off).json()
    assert (created["days_of_week"], created["specific_date"]) == (None, "2026-10-20")

    assert client.post("/api/routine-blocks", json={**base, "days_of_week": []}).status_code == 422
    no_date = {**base, "repeat_weekly": False}
    assert client.post("/api/routine-blocks", json=no_date).status_code == 422


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
        "/api/dashboard/agenda", params={"date": "2026-10-19", "today": "2026-10-21"}
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
    assert [d["is_today"] for d in agenda["week"]] == [
        False,
        False,
        True,
        False,
        False,
        False,
        False,
    ]
    assert agenda["sections"][0]["items"][0]["block"]["id"] == gym["id"]

    # Jueves: solo los hábitos diarios, ninguno hecho
    thursday = client.get(
        "/api/dashboard/agenda", params={"date": "2026-10-22", "today": "2026-10-22"}
    ).json()
    assert [i["title"] for s in thursday["sections"] for i in s["items"]] == ["Meditar", "Agua"]
    assert (thursday["completed"], thursday["total"], thursday["pct"]) == (0, 2, 0)
