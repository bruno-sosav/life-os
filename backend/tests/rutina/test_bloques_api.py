from fastapi.testclient import TestClient

from tests.rutina.ayuda import MONDAY, agenda, agenda_done


def test_routine_blocks_and_completions(client: TestClient) -> None:
    block = {"days_of_week": [0, 3], "hour_start": 7, "hour_end": 8, "activity": "Gym"}
    created = client.post("/api/routine-blocks", json=block).json()

    updated = client.put(f"/api/routine-blocks/{created['id']}", json={**block, "hour_end": 9})
    assert updated.json()["hour_end"] == 9

    toggle = {"block_id": created["id"], "date": MONDAY, "completed": True}
    assert client.put("/api/routine-completions", json=toggle).status_code == 204
    client.put("/api/routine-completions", json=toggle)  # idempotente
    assert agenda_done(client, created["id"]) is True
    assert agenda(client)["completed"] == 1

    client.put("/api/routine-completions", json={**toggle, "completed": False})
    assert agenda_done(client, created["id"]) is False


def test_routine_block_schedule_rules(client: TestClient) -> None:
    base = {"hour_start": 7, "hour_end": 8, "activity": "Gym"}
    multi = client.post("/api/routine-blocks", json={**base, "days_of_week": [3, 1, 3]}).json()
    assert multi["days_of_week"] == [1, 3]

    one_off = {**base, "repeat_weekly": False, "specific_date": "2026-10-20", "days_of_week": [1]}
    created = client.post("/api/routine-blocks", json=one_off).json()
    assert (created["days_of_week"], created["specific_date"]) == (None, "2026-10-20")

    assert client.post("/api/routine-blocks", json={**base, "days_of_week": []}).status_code == 422
    no_date = {**base, "repeat_weekly": False}
    assert client.post("/api/routine-blocks", json=no_date).status_code == 422


def test_block_categories_are_free_labels(client: TestClient) -> None:
    base = {"hour_start": 7, "hour_end": 8, "activity": "X", "days_of_week": [0]}
    for category in ("🎸 Música", " 🎸 Música ", "Estudio", None):
        client.post("/api/routine-blocks", json={**base, "category": category})
    assert client.get("/api/routine-blocks/categories").json() == ["🎸 Música", "Estudio"]

    too_long = {**base, "category": "x" * 31}
    assert client.post("/api/routine-blocks", json=too_long).status_code == 422
