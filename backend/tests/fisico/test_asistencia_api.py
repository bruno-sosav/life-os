from typing import Any

from fastapi.testclient import TestClient

from tests.fisico.ayuda import WEDNESDAY, create_activity, create_session


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
