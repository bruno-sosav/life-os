from collections.abc import Callable

from fastapi.testclient import TestClient


def test_analytics_summary_endpoint(
    client: TestClient, backdate_habits: Callable[[], None]
) -> None:
    habit = client.post("/api/habits", json={"name": "Leer"}).json()
    backdate_habits()
    for day in ("2026-10-12", "2026-10-13", "2026-10-14"):
        client.put(
            "/api/habit-logs", json={"habit_id": habit["id"], "date": day, "completed": True}
        )
    gym = client.post("/api/activities", json={"name": "Gym", "emoji": "🏋️"}).json()
    client.post("/api/sessions", json={"activity_id": gym["id"], "date": "2026-10-13"})
    client.put("/api/weight-logs/2026-10-14", json={"weight_kg": 80})

    summary = client.get("/api/analytics/summary", params={"today": "2026-10-14"}).json()
    assert (summary["week_start"], summary["week_end"]) == ("2026-10-12", "2026-10-18")
    # Hasta hoy (miércoles) tocaban 3 días y se hicieron los 3; la semana anterior, 0 de 7
    compliance = summary["compliance"]
    assert (compliance["pct"], compliance["prev_pct"], compliance["delta"]) == (100, 0, 100)
    assert summary["kpis"]["current_streak"] == 3
    assert summary["weight_series"] == [{"date": "2026-10-14", "kg": 80.0}]
    assert summary["activity_distribution"] == [
        {"id": gym["id"], "name": "Gym", "emoji": "🏋️", "color": "#0A84FF", "count": 1}
    ]
    history = summary["compliance_history"]
    assert len(history) == 12 and history[-1] == {
        "week_start": "2026-10-12",
        "pct": 100,
        "is_current": True,
    }

    previous = client.get(
        "/api/analytics/summary", params={"today": "2026-10-14", "week_offset": 1}
    ).json()
    assert previous["week_start"] == "2026-10-05" and previous["compliance"]["pct"] == 0
    assert (
        client.get(
            "/api/analytics/summary", params={"today": "2026-10-14", "week_offset": -1}
        ).status_code
        == 422
    )
