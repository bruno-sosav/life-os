from fastapi.testclient import TestClient

from tests.negocio.ayuda import board, create_project, create_task


def test_new_tasks_go_to_the_end_of_their_column(client: TestClient) -> None:
    project = create_project(client)
    for title in ("A", "B", "C"):
        create_task(client, project, title)
    create_task(client, project, "Lista", status="hecho")
    assert board(client, project) == {
        "pendiente": ["A", "B", "C"],
        "en_progreso": [],
        "hecho": ["Lista"],
    }


def test_move_reorders_within_a_column(client: TestClient) -> None:
    project = create_project(client)
    a, _, c = (create_task(client, project, t) for t in ("A", "B", "C"))
    client.put(f"/api/tasks/{c['id']}/move", json={"status": "pendiente", "position": 0})
    assert board(client, project)["pendiente"] == ["C", "A", "B"]
    client.put(f"/api/tasks/{a['id']}/move", json={"status": "pendiente", "position": 99})
    assert board(client, project)["pendiente"] == ["C", "B", "A"]  # más allá del final: al final


def test_move_to_another_column_and_completed_at(client: TestClient) -> None:
    project = create_project(client)
    a = create_task(client, project, "A")
    create_task(client, project, "X", status="hecho")
    create_task(client, project, "Y", status="hecho")

    moved = client.put(f"/api/tasks/{a['id']}/move", json={"status": "hecho", "position": 1})
    assert moved.json()["completed_at"].endswith("Z")
    assert board(client, project) == {"pendiente": [], "en_progreso": [], "hecho": ["X", "A", "Y"]}

    back = client.put(f"/api/tasks/{a['id']}/move", json={"status": "pendiente", "position": 0})
    assert back.json()["completed_at"] is None


def test_changing_status_in_the_form_goes_to_the_end(client: TestClient) -> None:
    project = create_project(client)
    a = create_task(client, project, "A")
    create_task(client, project, "B", status="en_progreso")
    client.patch(f"/api/tasks/{a['id']}", json={"status": "en_progreso"})
    assert board(client, project)["en_progreso"] == ["B", "A"]

    other = create_project(client, "Otro")
    client.patch(f"/api/tasks/{a['id']}", json={"project_id": other})
    assert board(client, other)["en_progreso"] == ["A"]


def test_task_validation(client: TestClient) -> None:
    project = create_project(client)
    task = {"title": "X", "project_id": project}
    assert client.post("/api/tasks", json={"title": "Sin proyecto"}).status_code == 422
    assert client.post("/api/tasks", json={**task, "project_id": "nope"}).status_code == 422
    assert client.post("/api/tasks", json={**task, "status": "bloqueada"}).status_code == 422
    assert client.post("/api/tasks", json={**task, "priority": "urgente"}).status_code == 422

    created = create_task(client, project, "X")
    url = f"/api/tasks/{created['id']}"
    assert client.patch(url, json={"project_id": None}).status_code == 422
    assert client.put(f"{url}/move", json={"status": "hecho", "position": -1}).status_code == 422
    assert client.get("/api/tasks/board", params={"project_id": "nope"}).status_code == 422
    assert client.delete("/api/tasks/nope").status_code == 404
