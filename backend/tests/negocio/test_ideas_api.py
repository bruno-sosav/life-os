from fastapi.testclient import TestClient


def test_business_ideas(client: TestClient) -> None:
    idea = client.post(
        "/api/business-ideas", json={"title": "App de cortes", "tags": ["producto", "growth"]}
    ).json()
    assert idea["tags"] == ["producto", "growth"]
    client.delete(f"/api/business-ideas/{idea['id']}")
    assert client.get("/api/business-ideas").json() == []
