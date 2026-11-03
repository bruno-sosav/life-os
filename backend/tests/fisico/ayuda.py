"""Helpers compartidos por los tests de Físico."""

from typing import Any

from fastapi.testclient import TestClient

WEDNESDAY = "2026-10-14"  # la semana va del 12 al 18


def create_activity(client: TestClient, **fields: Any) -> dict[str, Any]:
    response = client.post("/api/activities", json={"name": "Gym", **fields})
    assert response.status_code == 201, response.json()
    data: dict[str, Any] = response.json()
    return data


def gym(client: TestClient) -> dict[str, Any]:
    return create_activity(
        client,
        fields=[
            {"name": "Rutina", "type": "texto"},
            {"name": "Ejercicios", "type": "ejercicios"},
        ],
    )


def running(client: TestClient) -> dict[str, Any]:
    return create_activity(
        client,
        name="Correr",
        fields=[
            {"name": "Distancia", "type": "numero", "unit": "km"},
            {"name": "Sensación", "type": "escala"},
            {"name": "Terreno", "type": "opcion", "options": ["calle", "pista", " calle "]},
            {"name": "Llovió", "type": "si_no"},
        ],
    )


def field_id(activity: dict[str, Any], name: str) -> str:
    return str(next(f["id"] for f in activity["fields"] if f["name"] == name))


def create_session(client: TestClient, **fields: Any) -> dict[str, Any]:
    response = client.post("/api/sessions", json={"date": "2026-10-12", **fields})
    assert response.status_code == 201, response.json()
    data: dict[str, Any] = response.json()
    return data
