from typing import Any

from fastapi.testclient import TestClient

from tests.rutina.ayuda import MONDAY


def test_weekly_review_upsert(client: TestClient) -> None:
    def review() -> Any:
        params = {"today": "2026-10-14"}
        return client.get("/api/dashboard/weekly-review", params=params).json()["review"]

    assert review() is None
    client.put(f"/api/weekly-reviews/{MONDAY}", json={"went_well": "Gym 4 veces"})
    client.put(f"/api/weekly-reviews/{MONDAY}", json={"went_well": "Gym 5 veces"})
    assert review()["went_well"] == "Gym 5 veces"
