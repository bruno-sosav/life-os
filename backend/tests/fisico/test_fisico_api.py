from fastapi.testclient import TestClient


def create_gym_session(client: TestClient, **fields: object) -> dict[str, object]:
    response = client.post("/api/gym/sessions", json={"date": "2026-10-12", **fields})
    assert response.status_code == 201
    data: dict[str, object] = response.json()
    return data


def test_gym_session_with_exercises(client: TestClient) -> None:
    created = create_gym_session(
        client,
        routine_name="Push",
        exercises=[
            {"exercise_name": "Press banca", "sets": 3, "reps": 10, "weight_kg": 60.5},
            {"exercise_name": "Fondos", "sets": 3, "reps": 12},
        ],
    )
    sessions = client.get("/api/gym/sessions").json()
    assert len(sessions) == 1
    assert {e["exercise_name"] for e in sessions[0]["exercises"]} == {"Press banca", "Fondos"}
    assert any(e["weight_kg"] == 60.5 for e in sessions[0]["exercises"])  # número, no string

    patched = client.patch(f"/api/gym/sessions/{created['id']}", json={"attended": False})
    assert patched.json()["attended"] is False
    assert len(patched.json()["exercises"]) == 2

    assert client.delete(f"/api/gym/sessions/{created['id']}").status_code == 204
    assert client.get("/api/gym/exercises/names").json() == []  # cascade


def test_gym_sessions_newest_first(client: TestClient) -> None:
    create_gym_session(client, date="2026-10-10")
    create_gym_session(client, date="2026-10-14")
    dates = [s["date"] for s in client.get("/api/gym/sessions").json()]
    assert dates == ["2026-10-14", "2026-10-10"]


def test_exercise_names_and_progression(client: TestClient) -> None:
    create_gym_session(
        client,
        date="2026-10-05",
        exercises=[
            {"exercise_name": "Sentadilla", "sets": 3, "reps": 5, "weight_kg": 80},
            {"exercise_name": "Sentadilla", "sets": 1, "reps": 3, "weight_kg": 90},
        ],
    )
    create_gym_session(
        client,
        date="2026-10-12",
        exercises=[{"exercise_name": "sentadilla", "sets": 3, "reps": 5, "weight_kg": 85}],
    )
    create_gym_session(client, exercises=[{"exercise_name": "Remo", "weight_kg": 50}])

    names = client.get("/api/gym/exercises/names").json()
    assert "Remo" in names

    points = client.get("/api/gym/exercises/progression", params={"name": "SENTADILLA"}).json()
    assert points == [
        {"date": "2026-10-05", "max_weight_kg": 90.0, "volume_kg": 1470.0},
        {"date": "2026-10-12", "max_weight_kg": 85.0, "volume_kg": 1275.0},
    ]


def test_gym_validation(client: TestClient) -> None:
    bad = {"date": "2026-10-12", "exercises": [{"exercise_name": ""}]}
    assert client.post("/api/gym/sessions", json=bad).status_code == 422
    assert client.patch("/api/gym/sessions/no-existe", json={"attended": True}).status_code == 404


def test_mma_crud(client: TestClient) -> None:
    payload = {"date": "2026-10-12", "session_type": "sparring", "notes": "Buen ritmo"}
    created = client.post("/api/mma/sessions", json=payload).json()
    assert created["attended"] is True

    patched = client.patch(f"/api/mma/sessions/{created['id']}", json={"attended": False})
    assert patched.json()["attended"] is False
    assert patched.json()["session_type"] == "sparring"

    client.delete(f"/api/mma/sessions/{created['id']}")
    assert client.get("/api/mma/sessions").json() == []


def test_weight_log_upsert_and_range(client: TestClient) -> None:
    client.put("/api/weight-logs/2026-09-01", json={"weight_kg": 82})
    client.put("/api/weight-logs/2026-10-12", json={"weight_kg": 80.4})
    client.put("/api/weight-logs/2026-10-12", json={"weight_kg": 80.2, "notes": "en ayunas"})

    logs = client.get("/api/weight-logs", params={"start": "2026-10-01"}).json()
    assert [(log["date"], log["weight_kg"], log["notes"]) for log in logs] == [
        ("2026-10-12", 80.2, "en ayunas")
    ]
    assert len(client.get("/api/weight-logs").json()) == 2
    assert client.put("/api/weight-logs/2026-10-13", json={"weight_kg": 0}).status_code == 422


def test_nutrition_log_upsert(client: TestClient) -> None:
    day = {"quality_score": 4, "meals_count": 3, "water_liters": 2.5}
    client.put("/api/nutrition-logs/2026-10-12", json=day)
    client.put("/api/nutrition-logs/2026-10-12", json={**day, "quality_score": 5})

    logs = client.get("/api/nutrition-logs", params={"start": "2026-10-12"}).json()
    assert [(log["quality_score"], log["water_liters"]) for log in logs] == [(5, 2.5)]
    assert (
        client.put("/api/nutrition-logs/2026-10-13", json={"quality_score": 6}).status_code == 422
    )
