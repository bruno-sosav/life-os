from fastapi.testclient import TestClient


def test_goals_by_month(client: TestClient) -> None:
    goal = client.post("/api/goals", json={"title": "10 clientes", "month": "2026-10-18"}).json()
    assert goal["month"] == "2026-10-01"
    client.post("/api/goals", json={"title": "Otro mes", "month": "2026-11-03"})

    october = client.get("/api/goals", params={"month": "2026-10-31"}).json()
    assert [g["title"] for g in october] == ["10 clientes"]

    full = client.patch(f"/api/goals/{goal['id']}", json={"progress": 100}).json()
    assert full["completed"] is True
    partial = client.patch(f"/api/goals/{goal['id']}", json={"progress": 40}).json()
    assert partial["completed"] is False
    assert client.patch(f"/api/goals/{goal['id']}", json={"progress": 101}).status_code == 422
