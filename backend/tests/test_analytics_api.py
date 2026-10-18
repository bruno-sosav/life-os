from fastapi.testclient import TestClient


def test_analytics_data_shape_and_windows(client: TestClient) -> None:
    habit = client.post("/api/habits", json={"name": "Leer"}).json()
    client.put(
        "/api/habit-logs", json={"habit_id": habit["id"], "date": "2026-10-12", "completed": True}
    )
    client.put(
        "/api/habit-logs", json={"habit_id": habit["id"], "date": "2026-01-01", "completed": True}
    )
    client.put("/api/weight-logs/2025-01-01", json={"weight_kg": 85.5})
    client.put("/api/mood-logs/2026-10-10", json={"mood_score": 4, "sleep_hours": 7.5})
    client.post(
        "/api/books", json={"title": "Libro", "status": "leido", "finished_at": "2026-03-01"}
    )
    client.post("/api/finance/income", json={"month": "2026-05-01", "amount": 1000})
    client.post(
        "/api/finance/income", json={"month": "2026-04-30", "amount": 999}
    )  # fuera de 6 meses
    client.post("/api/journal-entries", json={"date": "2026-10-12", "content": "hola"})

    data = client.get("/api/analytics/data", params={"today": "2026-10-18"}).json()

    assert [h["name"] for h in data["habits"]] == ["Leer"]
    assert [log["date"] for log in data["habit_logs"]] == ["2026-10-12"]  # ventana de 90 días
    assert data["weight"] == [{"date": "2025-01-01", "weight_kg": 85.5}]  # todo el historial
    assert data["mood"] == [{"date": "2026-10-10", "mood_score": 4, "sleep_hours": 7.5}]
    assert data["books"] == [{"status": "leido", "finished_at": "2026-03-01"}]
    assert data["finance_income"] == [{"month": "2026-05-01", "amount": 1000.0}]
    assert data["journal_entries"][0]["created_at"].endswith("Z")
