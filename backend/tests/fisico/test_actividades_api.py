from typing import Any

from fastapi.testclient import TestClient

from tests.fisico.ayuda import field_id, running


def test_activity_crud_and_pause(client: TestClient) -> None:
    run = running(client)
    assert field_id(run, "Distancia")  # cada campo recibe su id
    assert run["fields"][2]["options"] == ["calle", "pista"]  # sin vacíos ni repetidos

    paused = client.patch(f"/api/activities/{run['id']}", json={"active": False}).json()
    assert paused["active"] is False and len(paused["fields"]) == 4
    assert client.get("/api/activities", params={"active": True}).json() == []
    assert len(client.get("/api/activities").json()) == 1

    assert client.delete(f"/api/activities/{run['id']}").status_code == 204
    assert client.get("/api/activities").json() == []


def test_removed_fields_are_archived_and_types_are_fixed(client: TestClient) -> None:
    run = running(client)
    distance = next(f for f in run["fields"] if f["name"] == "Distancia")
    patched = client.patch(
        f"/api/activities/{run['id']}",
        json={"fields": [distance, {"name": "Minutos", "type": "numero"}]},
    ).json()
    by_name = {f["name"]: f for f in patched["fields"]}
    assert by_name["Distancia"]["archived"] is False and by_name["Minutos"]["archived"] is False
    assert all(by_name[n]["archived"] for n in ("Sensación", "Terreno", "Llovió"))

    retyped = {**distance, "type": "texto"}
    response = client.patch(f"/api/activities/{run['id']}", json={"fields": [retyped]})
    assert response.status_code == 422


def test_activity_validation(client: TestClient) -> None:
    def status(fields: list[dict[str, Any]]) -> int:
        response = client.post("/api/activities", json={"name": "X", "fields": fields})
        return int(response.status_code)

    assert status([{"name": "Tipo", "type": "opcion"}]) == 422  # opción sin opciones
    assert status([{"name": "Tipo", "type": "color"}]) == 422  # tipo desconocido
    two_lists = [{"name": "A", "type": "ejercicios"}, {"name": "B", "type": "ejercicios"}]
    assert status(two_lists) == 422
    body = {"name": "X", "habit_id": "no-existe"}
    assert client.post("/api/activities", json=body).status_code == 422
