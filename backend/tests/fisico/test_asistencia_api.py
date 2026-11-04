from fastapi.testclient import TestClient

from tests.fisico.ayuda import WEDNESDAY, create_activity, create_session


def test_week_shows_every_type_trained_each_day(client: TestClient) -> None:
    gym, calistenia = (
        create_activity(client, name="Gym"),
        create_activity(client, name="Calistenia"),
    )
    create_session(client, activity_id=gym["id"], date="2026-10-12")
    create_session(client, activity_id=calistenia["id"], date="2026-10-12")
    create_session(client, activity_id=gym["id"], date="2026-10-14")
    create_session(client, activity_id=gym["id"], date="2026-10-16", attended=False)

    week = client.get("/api/training/week", params={"today": WEDNESDAY}).json()
    assert week["count"] == 2
    assert [d["date"] for d in week["days"]][0::6] == ["2026-10-12", "2026-10-18"]
    assert sorted(week["days"][0]["activity_ids"]) == sorted([gym["id"], calistenia["id"]])
    assert week["days"][2]["activity_ids"] == [gym["id"]]
    assert week["days"][4]["activity_ids"] == []  # faltó: no cuenta


def test_month_counts_the_linked_habit(client: TestClient) -> None:
    habit = client.post("/api/habits", json={"name": "Correr"}).json()
    running = create_activity(client, name="Correr", habit_id=habit["id"])
    # Marcado desde el dashboard, sin sesión: igual es un día entrenado
    client.put(
        "/api/habit-logs", json={"habit_id": habit["id"], "date": "2026-10-13", "completed": True}
    )

    month = client.get("/api/training/month", params={"month": "2026-10-20"}).json()
    assert (month["count"], len(month["days"])) == (1, 31)
    assert month["days"][12] == {"date": "2026-10-13", "activity_ids": [running["id"]]}


def test_sessions_mark_and_unmark_the_linked_habit(client: TestClient) -> None:
    habit = client.post("/api/habits", json={"name": "Ir al gym"}).json()
    gym = create_activity(client, habit_id=habit["id"])

    def habit_done() -> bool:
        logs = client.get("/api/dashboard/agenda", params={"date": WEDNESDAY, "today": WEDNESDAY})
        items = [i for s in logs.json()["sections"] for i in s["items"]]
        return bool(next(i for i in items if i["id"] == habit["id"])["done"])

    first = create_session(client, activity_id=gym["id"], date=WEDNESDAY)
    second = create_session(client, activity_id=gym["id"], date=WEDNESDAY)
    assert habit_done()
    client.delete(f"/api/sessions/{first['id']}")
    assert habit_done()  # queda otra sesión ese día
    client.delete(f"/api/sessions/{second['id']}")
    assert not habit_done()
