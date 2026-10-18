from fastapi.testclient import TestClient


def test_book_crud(client: TestClient) -> None:
    created = client.post("/api/books", json={"title": "Meditaciones", "author": "Marco Aurelio"})
    assert created.status_code == 201
    book = created.json()
    assert book["status"] == "pendiente"

    patch = {"status": "leido", "rating": 5, "finished_at": "2026-10-12"}
    updated = client.patch(f"/api/books/{book['id']}", json=patch).json()
    assert (updated["status"], updated["rating"], updated["author"]) == (
        "leido",
        5,
        "Marco Aurelio",
    )

    assert client.delete(f"/api/books/{book['id']}").status_code == 204
    assert client.get("/api/books").json() == []


def test_book_validation(client: TestClient) -> None:
    assert client.post("/api/books", json={"title": "X", "status": "abandonado"}).status_code == 422
    assert client.post("/api/books", json={"title": "X", "rating": 6}).status_code == 422
    assert client.post("/api/books", json={"title": ""}).status_code == 422


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

    weekly = client.get(
        "/api/dashboard/weekly-stats", params={"week_start": "2026-10-12", "today": "2026-10-14"}
    ).json()
    assert weekly["avg_mood"] == 4.5


def test_journal_entries(client: TestClient) -> None:
    first = client.post(
        "/api/journal-entries",
        json={"date": "2026-10-12", "content": "Primer día", "mood_emoji": "🙂"},
    ).json()
    client.post("/api/journal-entries", json={"date": "2026-10-13", "content": "Segundo"})
    entries = client.get("/api/journal-entries").json()
    assert len(entries) == 2
    assert entries[-1]["mood_emoji"] in ("🙂", None)

    client.delete(f"/api/journal-entries/{first['id']}")
    assert [e["content"] for e in client.get("/api/journal-entries").json()] == ["Segundo"]
    assert (
        client.post("/api/journal-entries", json={"date": "2026-10-13", "content": ""}).status_code
        == 422
    )


def test_ideas(client: TestClient) -> None:
    idea = client.post(
        "/api/ideas", json={"text": "La disciplina gana", "author": "Anónimo", "tag": "frase"}
    ).json()
    assert idea["tag"] == "frase"
    assert client.post("/api/ideas", json={"text": "X", "tag": "otra"}).status_code == 422

    client.delete(f"/api/ideas/{idea['id']}")
    assert client.get("/api/ideas").json() == []
