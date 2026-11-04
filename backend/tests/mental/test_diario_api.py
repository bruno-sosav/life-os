from fastapi.testclient import TestClient


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
