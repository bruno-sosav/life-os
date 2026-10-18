from fastapi.testclient import TestClient


def test_projects_and_task_filter(client: TestClient) -> None:
    project = client.post("/api/projects", json={"name": "Stratus Cuts"}).json()
    assert project["emoji"] == "📁"

    client.post("/api/tasks", json={"title": "Landing", "project_id": project["id"]})
    client.post("/api/tasks", json={"title": "Suelta"})
    assert len(client.get("/api/tasks").json()) == 2
    filtered = client.get("/api/tasks", params={"project_id": project["id"]}).json()
    assert [t["title"] for t in filtered] == ["Landing"]

    client.delete(f"/api/projects/{project['id']}")
    assert all(t["project_id"] is None for t in client.get("/api/tasks").json())


def test_task_completed_at_follows_status(client: TestClient) -> None:
    task = client.post("/api/tasks", json={"title": "Deploy"}).json()
    assert (task["status"], task["priority"], task["completed_at"]) == ("pendiente", "media", None)

    done = client.patch(f"/api/tasks/{task['id']}", json={"status": "hecho"}).json()
    assert done["completed_at"].endswith("Z")

    back = client.patch(f"/api/tasks/{task['id']}", json={"status": "en_progreso"}).json()
    assert back["completed_at"] is None


def test_task_validation(client: TestClient) -> None:
    assert client.post("/api/tasks", json={"title": "X", "status": "bloqueada"}).status_code == 422
    assert client.post("/api/tasks", json={"title": "X", "priority": "urgente"}).status_code == 422
    assert client.post("/api/tasks", json={"title": "X", "project_id": "nope"}).status_code == 422
    assert client.delete("/api/tasks/nope").status_code == 404


def test_business_ideas(client: TestClient) -> None:
    idea = client.post(
        "/api/business-ideas", json={"title": "App de cortes", "tags": ["producto", "growth"]}
    ).json()
    assert idea["tags"] == ["producto", "growth"]
    client.delete(f"/api/business-ideas/{idea['id']}")
    assert client.get("/api/business-ideas").json() == []


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
