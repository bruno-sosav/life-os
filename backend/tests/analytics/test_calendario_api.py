from collections.abc import Callable

from fastapi.testclient import TestClient


def test_month_calendar(client: TestClient, backdate_habits: Callable[[], None]) -> None:
    leer = client.post("/api/habits", json={"name": "Leer"}).json()
    agua = client.post("/api/habits", json={"name": "Agua"}).json()
    backdate_habits()
    for habit, day in ((leer, "2026-10-12"), (agua, "2026-10-12"), (leer, "2026-10-13")):
        log = {"habit_id": habit["id"], "date": day, "completed": True}
        client.put("/api/habit-logs", json=log)

    month = client.get(
        "/api/analytics/calendar", params={"month": "2026-10-20", "today": "2026-10-14"}
    ).json()
    days = {d["date"]: d for d in month["days"]}
    assert len(days) == 31
    assert days["2026-10-12"] == {
        "date": "2026-10-12",
        "status": "cumplido",
        "done": 2,
        "expected": 2,
        "pct": 100,
    }
    assert (days["2026-10-13"]["status"], days["2026-10-13"]["pct"]) == ("parcial", 50)
    assert days["2026-10-01"]["status"] == "sin_cumplir"
    # Hoy todavía no terminó y los días que vienen no llegaron
    assert {days["2026-10-14"]["status"], days["2026-10-31"]["status"]} == {"pendiente"}

    # Octubre arranca un jueves: la primera semana es la del lunes 28 de septiembre
    weeks = {w["week_start"]: w["pct"] for w in month["weeks"]}
    assert list(weeks) == ["2026-09-28", "2026-10-05", "2026-10-12", "2026-10-19", "2026-10-26"]
    assert (weeks["2026-10-12"], weeks["2026-10-19"]) == (50, None)  # 3 de 6 hasta hoy
    assert (month["cumplido"], month["parcial"], month["sin_cumplir"]) == (1, 1, 11)
