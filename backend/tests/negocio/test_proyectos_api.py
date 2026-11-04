from fastapi.testclient import TestClient

from tests.negocio.ayuda import board, create_project, create_task


def test_each_project_has_its_own_board(client: TestClient) -> None:
    stratus, cuts = create_project(client, "Stratus"), create_project(client, "Cuts")
    create_task(client, stratus, "Landing")
    create_task(client, cuts, "Turnero")
    assert board(client, stratus)["pendiente"] == ["Landing"]
    assert board(client, cuts)["pendiente"] == ["Turnero"]


def test_deleting_a_project_deletes_its_board(client: TestClient) -> None:
    project = create_project(client)
    task = create_task(client, project, "Landing")
    assert client.delete(f"/api/projects/{project}").status_code == 204
    assert client.delete(f"/api/tasks/{task['id']}").status_code == 404


def test_rename_project(client: TestClient) -> None:
    project = create_project(client, "Stratus")
    url = f"/api/projects/{project}"
    renamed = client.patch(url, json={"name": "Stratus Cuts", "color": "#7C5CFF"}).json()
    assert (renamed["name"], renamed["color"]) == ("Stratus Cuts", "#7C5CFF")
    assert client.patch(url, json={"name": ""}).status_code == 422
    assert client.patch("/api/projects/nope", json={"name": "X"}).status_code == 404
