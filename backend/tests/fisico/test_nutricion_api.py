from fastapi.testclient import TestClient


def test_nutrition_log_upsert(client: TestClient) -> None:
    day = {"quality_score": 4, "meals_count": 3, "water_liters": 2.5}
    client.put("/api/nutrition-logs/2026-10-12", json=day)
    client.put("/api/nutrition-logs/2026-10-12", json={**day, "quality_score": 5})

    logs = client.get("/api/nutrition-logs", params={"start": "2026-10-12"}).json()
    assert [(log["quality_score"], log["water_liters"]) for log in logs] == [(5, 2.5)]
    assert (
        client.put("/api/nutrition-logs/2026-10-13", json={"quality_score": 6}).status_code == 422
    )


def test_nutrition_average_last_7_days(client: TestClient) -> None:
    assert client.get("/api/nutrition-logs/average", params={"today": "2026-10-14"}).json() == {
        "avg_quality": None
    }
    for day, score in (("2026-10-07", 1), ("2026-10-08", 4), ("2026-10-14", 5)):
        client.put(f"/api/nutrition-logs/{day}", json={"quality_score": score})
    client.put("/api/nutrition-logs/2026-10-13", json={"meals_count": 3})  # sin calidad: no cuenta
    average = client.get("/api/nutrition-logs/average", params={"today": "2026-10-14"}).json()
    assert average == {"avg_quality": 4.5}  # el 07 queda afuera
