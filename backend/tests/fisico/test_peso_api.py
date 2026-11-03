from fastapi.testclient import TestClient


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


def test_weight_goal(client: TestClient) -> None:
    assert client.get("/api/weight-goal").json() == {"weight_kg": None}
    client.put("/api/weight-goal", json={"weight_kg": 80})
    client.put("/api/weight-goal", json={"weight_kg": 78.5})  # pisa la misma fila
    assert client.get("/api/weight-goal").json() == {"weight_kg": 78.5}
    client.put("/api/weight-goal", json={"weight_kg": None})
    assert client.get("/api/weight-goal").json() == {"weight_kg": None}
    assert client.put("/api/weight-goal", json={"weight_kg": 0}).status_code == 422
