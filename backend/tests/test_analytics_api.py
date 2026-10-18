from fastapi.testclient import TestClient


def test_analytics_summary_endpoint(client: TestClient) -> None:
    habit = client.post("/api/habits", json={"name": "Stratus"}).json()
    for day in ("2026-10-12", "2026-10-13", "2026-10-14"):
        client.put(
            "/api/habit-logs", json={"habit_id": habit["id"], "date": day, "completed": True}
        )
    client.post("/api/gym/sessions", json={"date": "2026-10-13"})
    client.put("/api/weight-logs/2026-10-14", json={"weight_kg": 80})

    summary = client.get("/api/analytics/summary", params={"today": "2026-10-14"}).json()
    assert (summary["week_start"], summary["week_end"]) == ("2026-10-12", "2026-10-18")
    # 3/7 hábitos → 21 · 1/5 entrenos → 6 · 3/5 días Stratus → 12
    assert summary["bruce"]["total"] == 39
    assert summary["kpis"]["current_streak"] == 3
    assert summary["weight_series"] == [{"date": "2026-10-14", "kg": 80.0}]
    assert summary["gym_vs_mma"] == {"gym": 1, "mma": 0}
    assert len(summary["bruce_history"]) == 12 and summary["bruce_history"][-1]["is_current"]

    previous = client.get(
        "/api/analytics/summary", params={"today": "2026-10-14", "week_offset": 1}
    ).json()
    assert previous["week_start"] == "2026-10-05" and previous["bruce"]["total"] == 0
    assert (
        client.get(
            "/api/analytics/summary", params={"today": "2026-10-14", "week_offset": -1}
        ).status_code
        == 422
    )
