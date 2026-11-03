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


# ─── Actividades ────────────────────────────────────────────
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


# ─── Sesiones ───────────────────────────────────────────────
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
    names = client.get(f"/api/activities/{activity['id']}/exercises/names").json()
    assert names == []  # los ejercicios se borran con la sesión
    assert client.delete("/api/sessions/no-existe").status_code == 404


# ─── Gráficos ───────────────────────────────────────────────
def test_exercise_names_and_progression(client: TestClient) -> None:
    activity = gym(client)
    other = gym(client)  # otra actividad con lista de ejercicios: no se mezcla
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
        activity_id=activity["id"],
        exercises=[{"exercise_name": "sentadilla", "weight_kg": 85}],
    )
    create_session(client, activity_id=other["id"], exercises=[{"exercise_name": "Remo"}])

    base = f"/api/activities/{activity['id']}/exercises"
    assert client.get(f"{base}/names").json() == ["Sentadilla", "sentadilla"]
    points = client.get(f"{base}/progression", params={"name": "SENTADILLA"}).json()
    assert points == [{"date": "2026-10-05", "value": 90.0}, {"date": "2026-10-12", "value": 85.0}]


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


# ─── Asistencia y calendario ────────────────────────────────
def test_attendance_week_and_toggle_without_habit(client: TestClient) -> None:
    activity = create_activity(client, name="MMA")
    url = f"/api/activities/{activity['id']}"
    assert client.put(f"{url}/attendance/2026-10-13").json()["attended"] is True  # crea sesión
    week = client.get(f"{url}/week", params={"today": WEDNESDAY}).json()
    assert week["habit"] is None
    assert [d["date"] for d in week["days"]][0::6] == ["2026-10-12", "2026-10-18"]
    assert [d["attended"] for d in week["days"]] == [False, True, False, False, False, False, False]

    assert client.put(f"{url}/attendance/2026-10-13").json()["attended"] is False
    assert len(client.get("/api/sessions").json()) == 1  # desmarcar no borra la sesión


def test_attendance_uses_linked_habit(client: TestClient) -> None:
    habit = client.post("/api/habits", json={"name": "Ir al gym"}).json()
    activity = create_activity(client, habit_id=habit["id"])
    url = f"/api/activities/{activity['id']}"
    assert client.put(f"{url}/attendance/{WEDNESDAY}").json()["attended"] is True
    week = client.get(f"{url}/week", params={"today": WEDNESDAY}).json()
    assert week["habit"] == {"id": habit["id"], "name": "Ir al gym"}
    assert week["days"][2] == {"date": WEDNESDAY, "attended": True}
    assert client.get("/api/sessions").json() == []  # no toca las sesiones

    client.put(f"{url}/attendance/{WEDNESDAY}")
    week = client.get(f"{url}/week", params={"today": WEDNESDAY}).json()
    assert week["days"][2]["attended"] is False

    # Sin el hábito (borrado), vuelve a usar las sesiones
    client.delete(f"/api/habits/{habit['id']}")
    assert client.get(f"{url}/week", params={"today": WEDNESDAY}).json()["habit"] is None


def test_month_matches_week_with_linked_habit(client: TestClient) -> None:
    """Desmarcar no suma al contador; el hábito vinculado cuenta en el mes como en la semana."""
    habit = client.post("/api/habits", json={"name": "Correr"}).json()
    linked = create_activity(client, name="Correr", habit_id=habit["id"])
    loose = create_activity(client, name="Yoga")
    client.put(f"/api/activities/{linked['id']}/attendance/2026-10-13")
    for _ in range(2):
        client.put(f"/api/activities/{loose['id']}/attendance/2026-10-13")

    def month(activity: dict[str, Any]) -> dict[str, Any]:
        url = f"/api/activities/{activity['id']}/month"
        result: dict[str, Any] = client.get(url, params={"month": "2026-10-01"}).json()
        return result

    assert (month(linked)["count"], month(linked)["days"][12]["attended"]) == (1, True)
    assert month(loose)["count"] == 0


def test_activity_month(client: TestClient) -> None:
    activity = create_activity(client, name="MMA")
    for day, attended in (("2026-10-03", True), ("2026-10-20", False), ("2026-11-01", True)):
        create_session(client, activity_id=activity["id"], date=day, attended=attended)
    month = client.get(
        f"/api/activities/{activity['id']}/month", params={"month": "2026-10-15"}
    ).json()
    assert month["count"] == 1 and len(month["days"]) == 31
    assert (month["days"][2]["attended"], month["days"][19]["attended"]) == (True, False)
    assert month["days"][0]["attended"] is None
    assert (
        client.get("/api/activities/no-existe/month", params={"month": WEDNESDAY}).status_code
        == 404
    )


# ─── Peso / Nutrición ───────────────────────────────────────
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


def test_nutrition_log_upsert(client: TestClient) -> None:
    day = {"quality_score": 4, "meals_count": 3, "water_liters": 2.5}
    client.put("/api/nutrition-logs/2026-10-12", json=day)
    client.put("/api/nutrition-logs/2026-10-12", json={**day, "quality_score": 5})

    logs = client.get("/api/nutrition-logs", params={"start": "2026-10-12"}).json()
    assert [(log["quality_score"], log["water_liters"]) for log in logs] == [(5, 2.5)]
    assert (
        client.put("/api/nutrition-logs/2026-10-13", json={"quality_score": 6}).status_code == 422
    )


def test_nutrition_average_last_7_days(client: TestClient) -> None:
    assert client.get("/api/nutrition-logs/average", params={"today": "2026-10-14"}).json() == {
        "avg_quality": None
    }
    for day, score in (("2026-10-07", 1), ("2026-10-08", 4), ("2026-10-14", 5)):
        client.put(f"/api/nutrition-logs/{day}", json={"quality_score": score})
    client.put("/api/nutrition-logs/2026-10-13", json={"meals_count": 3})  # sin calidad: no cuenta
    average = client.get("/api/nutrition-logs/average", params={"today": "2026-10-14"}).json()
    assert average == {"avg_quality": 4.5}  # el 07 queda afuera


def test_weight_goal(client: TestClient) -> None:
    assert client.get("/api/weight-goal").json() == {"weight_kg": None}
    client.put("/api/weight-goal", json={"weight_kg": 80})
    client.put("/api/weight-goal", json={"weight_kg": 78.5})  # pisa la misma fila
    assert client.get("/api/weight-goal").json() == {"weight_kg": 78.5}
    client.put("/api/weight-goal", json={"weight_kg": None})
    assert client.get("/api/weight-goal").json() == {"weight_kg": None}
    assert client.put("/api/weight-goal", json={"weight_kg": 0}).status_code == 422
