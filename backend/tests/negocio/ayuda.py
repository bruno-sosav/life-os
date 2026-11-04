"""Helpers compartidos por los tests de Negocio."""

from typing import Any

from fastapi.testclient import TestClient


def create_project(client: TestClient, name: str = "Stratus") -> str:
    response = client.post("/api/projects", json={"name": name})
    assert response.status_code == 201, response.json()
    return str(response.json()["id"])


def create_task(client: TestClient, project_id: str, title: str, **fields: Any) -> dict[str, Any]:
    response = client.post("/api/tasks", json={"title": title, "project_id": project_id, **fields})
    assert response.status_code == 201, response.json()
    data: dict[str, Any] = response.json()
    return data


def board(client: TestClient, project_id: str) -> dict[str, list[str]]:
    """El tablero como títulos por columna, en orden."""
    response = client.get("/api/tasks/board", params={"project_id": project_id})
    return {column: [t["title"] for t in tasks] for column, tasks in response.json().items()}
