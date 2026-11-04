"""Helpers compartidos por los tests de Rutina."""

from typing import Any

from fastapi.testclient import TestClient

MONDAY = "2026-10-12"


def create_habit(client: TestClient, **fields: object) -> dict[str, object]:
    response = client.post("/api/habits", json={"name": "Leer", **fields})
    assert response.status_code == 201
    data: dict[str, object] = response.json()
    return data


def agenda(client: TestClient, day: str = MONDAY) -> dict[str, Any]:
    data: dict[str, Any] = client.get(
        "/api/dashboard/agenda", params={"date": day, "today": day}
    ).json()
    return data


def agenda_done(client: TestClient, item_id: object) -> bool:
    items = [it for section in agenda(client)["sections"] for it in section["items"]]
    return next(bool(it["done"]) for it in items if it["id"] == item_id)
