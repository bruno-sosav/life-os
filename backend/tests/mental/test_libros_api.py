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
