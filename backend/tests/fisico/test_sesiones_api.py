from typing import Any

from fastapi.testclient import TestClient

from tests.fisico.ayuda import create_session, field_id, gym, running


def test_session_values_are_validated(client: TestClient) -> None:
    run = running(client)
    values = {
        field_id(run, "Distancia"): 5,
        field_id(run, "Sensación"): 4,
        field_id(run, "Terreno"): "pista",
        field_id(run, "Llovió"): False,
    }
    created = create_session(client, activity_id=run["id"], values=values)
    assert created["values"][field_id(run, "Distancia")] == 5.0
    assert created["values"][field_id(run, "Llovió")] is False

    empty = create_session(client, activity_id=run["id"], values={field_id(run, "Terreno"): ""})
    assert empty["values"] == {}  # un valor vacío no se guarda

    def status(values: dict[str, Any], **extra: Any) -> int:
        body = {"activity_id": run["id"], "date": "2026-10-12", "values": values, **extra}
        return int(client.post("/api/sessions", json=body).status_code)

    assert status({field_id(run, "Sensación"): 7}) == 422
    assert status({field_id(run, "Sensación"): 3.5}) == 422
    assert status({field_id(run, "Distancia"): "cinco"}) == 422
    assert status({field_id(run, "Distancia"): True}) == 422
    assert status({field_id(run, "Terreno"): "montaña"}) == 422
    assert status({"campo-inventado": 1}) == 422
    assert status({}, exercises=[{"exercise_name": "Sentadilla"}]) == 422  # sin lista


def test_archived_field_rejects_new_values_but_keeps_old_ones(client: TestClient) -> None:
    run = running(client)
    distance = field_id(run, "Distancia")
    old = create_session(client, activity_id=run["id"], values={distance: 3})
    client.patch(f"/api/activities/{run['id']}", json={"fields": []})

    body = {"activity_id": run["id"], "date": "2026-10-13", "values": {distance: 4}}
    assert client.post("/api/sessions", json=body).status_code == 422
    sessions = client.get("/api/sessions", params={"activity_id": run["id"]}).json()
    assert sessions[0]["id"] == old["id"] and sessions[0]["values"] == {distance: 3.0}


def test_sessions_with_exercises(client: TestClient) -> None:
    activity = gym(client)
    created = create_session(
        client,
        activity_id=activity["id"],
        values={field_id(activity, "Rutina"): "Push"},
        exercises=[
            {"exercise_name": "Press banca", "sets": 3, "reps": 10, "weight_kg": 60.5},
            {"exercise_name": "Fondos", "sets": 3, "reps": 12},
        ],
    )
    create_session(client, activity_id=activity["id"], date="2026-10-14")
    sessions = client.get("/api/sessions", params={"activity_id": activity["id"]}).json()
    assert [s["date"] for s in sessions] == ["2026-10-14", "2026-10-12"]  # más nueva primero
    assert any(e["weight_kg"] == 60.5 for e in sessions[1]["exercises"])  # número, no string

    assert client.delete(f"/api/sessions/{created['id']}").status_code == 204
    names = client.get("/api/exercises/names").json()
    assert names == []  # los ejercicios se borran con la sesión
    assert client.delete("/api/sessions/no-existe").status_code == 404


def test_exercises_across_types(client: TestClient) -> None:
    activity, other = gym(client), gym(client)
    create_session(
        client,
        activity_id=activity["id"],
        date="2026-10-05",
        exercises=[
            {"exercise_name": "Sentadilla", "sets": 3, "reps": 5, "weight_kg": 80},
            {"exercise_name": "Sentadilla", "sets": 1, "reps": 3, "weight_kg": 90},
        ],
    )
    create_session(
        client,
        activity_id=other["id"],
        date="2026-10-12",
        exercises=[
            {"exercise_name": "sentadilla", "sets": 4, "reps": 6, "weight_kg": 85},
            {"exercise_name": "Remo", "sets": 3, "reps": 10},
        ],
    )

    # Sin distinguir mayúsculas y de cualquier tipo; el más usado primero
    names = client.get("/api/exercises/names").json()
    assert len(names) == 2 and names[0].lower() == "sentadilla" and names[1] == "Remo"

    last = client.get("/api/exercises/last", params={"name": " SENTADILLA "}).json()
    assert (last["date"], last["activity_id"]) == ("2026-10-12", other["id"])
    assert [(x["sets"], x["reps"], x["weight_kg"]) for x in last["sets"]] == [(4, 6, 85.0)]
    assert client.get("/api/exercises/last", params={"name": "Nunca"}).json() is None

    progression = client.get("/api/exercises/progression", params={"name": "sentadilla"}).json()
    assert progression["points"] == [
        {"date": "2026-10-05", "value": 90.0},
        {"date": "2026-10-12", "value": 85.0},
    ]
    assert progression["best"] == {"date": "2026-10-05", "value": 90.0}
    empty = client.get("/api/exercises/progression", params={"name": "Remo"}).json()
    assert empty["best"] is None


def test_field_series(client: TestClient) -> None:
    run = running(client)
    distance = field_id(run, "Distancia")
    create_session(client, activity_id=run["id"], date="2026-10-14", values={distance: 7.5})
    create_session(client, activity_id=run["id"], date="2026-10-12", values={distance: 5})
    create_session(client, activity_id=run["id"], date="2026-10-13")  # sin distancia: no suma

    series = client.get(f"/api/activities/{run['id']}/fields/{distance}/series").json()
    assert series == [{"date": "2026-10-12", "value": 5.0}, {"date": "2026-10-14", "value": 7.5}]
    terrain = field_id(run, "Terreno")
    response = client.get(f"/api/activities/{run['id']}/fields/{terrain}/series")
    assert response.status_code == 422  # una opción no se grafica
