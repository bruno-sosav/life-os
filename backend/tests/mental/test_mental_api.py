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
    library = client.get("/api/books/library", params={"today": "2026-10-14"}).json()
    assert library["shelves"] == {"pendiente": [], "leyendo": [], "leido": []}


def test_library_shelves_and_year_count(client: TestClient) -> None:
    def book(title: str, **fields: object) -> None:
        client.post("/api/books", json={"title": title, **fields})

    book("Pendiente")
    book("Leyendo", status="leyendo")
    book("Este año", status="leido", finished_at="2026-03-01")
    book("Año pasado", status="leido", finished_at="2025-12-31")
    book("Sin fecha", status="leido")

    library = client.get("/api/books/library", params={"today": "2026-10-14"}).json()
    shelves = {k: [b["title"] for b in v] for k, v in library["shelves"].items()}
    assert shelves["pendiente"] == ["Pendiente"] and shelves["leyendo"] == ["Leyendo"]
    assert len(shelves["leido"]) == 3
    assert (library["year"], library["read_this_year"]) == (2026, 1)


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

    weekly = client.get("/api/dashboard/weekly-review", params={"today": "2026-10-14"}).json()
    assert (weekly["avg_mood"], weekly["mood_level"]) == (4.5, "excelente")


def test_mood_average_last_7_days(client: TestClient) -> None:
    def average(today: str) -> object:
        return client.get("/api/mood-logs/average", params={"today": today}).json()["avg_mood"]

    assert average("2026-10-14") is None
    for day, score in (("2026-10-07", 1), ("2026-10-08", 4), ("2026-10-14", 3)):
        client.put(f"/api/mood-logs/{day}", json={"mood_score": score})
    assert average("2026-10-14") == 3.5  # el 07 queda afuera


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


def test_ideas_with_free_tags(client: TestClient) -> None:
    def idea(text: str, **fields: object) -> dict[str, object]:
        data: dict[str, object] = client.post("/api/ideas", json={"text": text, **fields}).json()
        return data

    quote = idea("La disciplina gana", author="Anónimo", tag="  💬 Frase ")
    assert quote["tag"] == "💬 Frase"  # sin espacios de más
    idea("Otra frase", tag="💬 Frase")
    assert idea("Sin etiqueta")["tag"] == "💡 Idea"
    assert client.post("/api/ideas", json={"text": "X", "tag": "  "}).status_code == 422

    tags = client.get("/api/ideas/tags").json()
    assert tags == [{"tag": "💬 Frase", "count": 2}, {"tag": "💡 Idea", "count": 1}]
    quotes = client.get("/api/ideas", params={"tag": "💬 Frase"}).json()
    assert {i["text"] for i in quotes} == {"La disciplina gana", "Otra frase"}

    client.delete(f"/api/ideas/{quote['id']}")
    assert len(client.get("/api/ideas").json()) == 2
