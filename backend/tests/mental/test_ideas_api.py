from fastapi.testclient import TestClient


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
