from fastapi.testclient import TestClient


def test_mood_log_upsert_and_weekly_stats(client: TestClient) -> None:
    client.put("/api/mood-logs/2026-10-12", json={"mood_score": 3, "sleep_hours": 7})
    client.put("/api/mood-logs/2026-10-12", json={"mood_score": 4, "energy_score": 5})
    client.put("/api/mood-logs/2026-10-13", json={"mood_score": 5, "sleep_hours": 7.5})

    logs = client.get("/api/mood-logs", params={"start": "2026-10-12"}).json()
    assert [(m["date"], m["mood_score"], m["sleep_hours"]) for m in logs] == [
        ("2026-10-12", 4, None),
        ("2026-10-13", 5, 7.5),
    ]
    assert client.put("/api/mood-logs/2026-10-14", json={"mood_score": 0}).status_code == 422

    weekly = client.get("/api/dashboard/weekly-review", params={"today": "2026-10-14"}).json()
    assert (weekly["avg_mood"], weekly["mood_level"]) == (4.5, "excelente")


def test_mood_average_last_7_days(client: TestClient) -> None:
    def average(today: str) -> object:
        return client.get("/api/mood-logs/average", params={"today": today}).json()["avg_mood"]

    assert average("2026-10-14") is None
    for day, score in (("2026-10-07", 1), ("2026-10-08", 4), ("2026-10-14", 3)):
        client.put(f"/api/mood-logs/{day}", json={"mood_score": score})
    assert average("2026-10-14") == 3.5  # el 07 queda afuera
