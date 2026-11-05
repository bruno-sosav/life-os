from typing import Any

from fastapi.testclient import TestClient

TODAY = "2026-10-14"  # miércoles; la semana arranca el lunes 12


def create_skill(client: TestClient, **fields: Any) -> dict[str, Any]:
    response = client.post("/api/skills", json={"name": "Inglés", **fields})
    assert response.status_code == 201, response.json()
    data: dict[str, Any] = response.json()
    return data


def practice(client: TestClient, skill_id: str, day: str, minutes: int) -> dict[str, Any]:
    response = client.post(
        "/api/practices", json={"skill_id": skill_id, "date": day, "minutes": minutes}
    )
    assert response.status_code == 201, response.json()
    data: dict[str, Any] = response.json()
    return data


def skills(client: TestClient) -> dict[str, dict[str, Any]]:
    response = client.get("/api/skills", params={"today": TODAY}).json()
    return {s["name"]: s for s in response}


def test_week_total_and_last_six_weeks(client: TestClient) -> None:
    ajedrez = create_skill(client, name="Ajedrez", type="Juego", weekly_goal_min=180)
    practice(client, ajedrez["id"], "2026-10-13", 20)
    practice(client, ajedrez["id"], "2026-10-14", 40)
    practice(client, ajedrez["id"], "2026-10-06", 30)  # semana anterior
    practice(client, ajedrez["id"], "2026-08-01", 15)  # suma al total, fuera del gráfico

    s = skills(client)["Ajedrez"]
    assert (s["week_minutes"], s["total_minutes"], s["last_practice"]) == (60, 105, "2026-10-14")
    assert (s["type"], s["weekly_goal_min"], s["stage"]) == ("Juego", 180, "practicando")
    assert [w["week_start"] for w in s["weeks"]][-2:] == ["2026-10-05", "2026-10-12"]
    assert [w["minutes"] for w in s["weeks"]][-2:] == [30, 60]
    assert client.get("/api/skills/types").json() == ["Juego"]


def test_order_by_stage_resources_and_books(client: TestClient) -> None:
    create_skill(client, name="Ciber", stage="la_tengo")
    paused = create_skill(client, name="Ventas", stage="en_pausa")
    ingles = create_skill(client, name="Inglés")
    assert list(skills(client)) == ["Inglés", "Ventas", "Ciber"]

    resource = {"kind": "curso", "name": "Duolingo", "url": "https://duolingo.com"}
    assert client.post(f"/api/skills/{ingles['id']}/resources", json=resource).status_code == 201
    client.post("/api/books", json={"title": "Grammar in Use", "skill_id": ingles["id"]})
    s = skills(client)["Inglés"]
    assert [r["name"] for r in s["resources"]] == ["Duolingo"]
    assert [b["title"] for b in s["books"]] == ["Grammar in Use"]

    client.patch(f"/api/skills/{paused['id']}", json={"stage": "practicando", "name": "Ventas B2B"})
    # Dentro de la misma etapa, en el orden en que las creaste
    assert list(skills(client))[:2] == ["Ventas B2B", "Inglés"]
    client.delete(f"/api/skills/{ingles['id']}")
    books = client.get("/api/books/library", params={"today": TODAY}).json()["shelves"]
    assert books["pendiente"][0]["skill_id"] is None  # el libro queda, sin skill


def test_practice_marks_the_linked_habit(client: TestClient) -> None:
    habit = client.post("/api/habits", json={"name": "Estudiar inglés"}).json()
    ingles = create_skill(client, habit_id=habit["id"])

    def habit_done() -> bool:
        agenda = client.get("/api/dashboard/agenda", params={"date": TODAY, "today": TODAY})
        items = [i for s in agenda.json()["sections"] for i in s["items"]]
        return bool(next(i for i in items if i["id"] == habit["id"])["done"])

    first = practice(client, ingles["id"], TODAY, 20)
    second = practice(client, ingles["id"], TODAY, 10)
    assert habit_done()
    client.delete(f"/api/practices/{first['id']}")
    assert habit_done()
    client.delete(f"/api/practices/{second['id']}")
    assert not habit_done()

    history = client.get(f"/api/skills/{ingles['id']}/practices").json()
    assert history == []


def test_skill_validation(client: TestClient) -> None:
    assert client.post("/api/skills", json={"name": ""}).status_code == 422
    assert client.post("/api/skills", json={"name": "X", "stage": "olvidada"}).status_code == 422
    assert client.post("/api/skills", json={"name": "X", "weekly_goal_min": 0}).status_code == 422
    assert client.post("/api/skills", json={"name": "X", "habit_id": "nope"}).status_code == 422
    skill = create_skill(client)
    bad = {"skill_id": skill["id"], "date": TODAY, "minutes": 0}
    assert client.post("/api/practices", json=bad).status_code == 422
    assert (
        client.post("/api/practices", json={**bad, "skill_id": "nope", "minutes": 5}).status_code
        == 422
    )
    assert client.post("/api/skills/nope/resources", json={"name": "X"}).status_code == 404
