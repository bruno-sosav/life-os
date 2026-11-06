from typing import Any

from fastapi.testclient import TestClient


def lists(client: TestClient) -> dict[str, dict[str, Any]]:
    return {lst["name"]: lst for lst in client.get("/api/lists").json()}


def texts(client: TestClient, name: str) -> list[str]:
    return [i["text"] for i in lists(client)[name]["items"]]


def test_lists_items_order_done_and_clear(client: TestClient) -> None:
    compras = client.post("/api/lists", json={"name": "Compras", "color": "#D95926"}).json()
    client.post("/api/lists", json={"name": "Quiero aprender", "for_learning": True})
    assert list(lists(client)) == ["Compras", "Quiero aprender"]
    assert lists(client)["Quiero aprender"]["for_learning"] is True

    for text in ("Proteína", "Auriculares", "Rodillera"):
        client.post(f"/api/lists/{compras['id']}/items", json={"text": text})
    assert texts(client, "Compras") == ["Rodillera", "Auriculares", "Proteína"]  # lo nuevo arriba

    rodillera = lists(client)["Compras"]["items"][0]
    client.patch(f"/api/list-items/{rodillera['id']}", json={"done": True, "note": "talle M"})
    assert texts(client, "Compras") == ["Auriculares", "Proteína", "Rodillera"]  # hechos al final

    proteina = lists(client)["Compras"]["items"][1]
    client.put(f"/api/list-items/{proteina['id']}/move", json={"position": 0})
    assert texts(client, "Compras") == ["Proteína", "Auriculares", "Rodillera"]

    client.delete(f"/api/lists/{compras['id']}/done")
    assert texts(client, "Compras") == ["Proteína", "Auriculares"]
    client.delete(f"/api/lists/{compras['id']}")
    assert list(lists(client)) == ["Quiero aprender"]


def test_unticked_item_goes_back_to_the_top(client: TestClient) -> None:
    lst = client.post("/api/lists", json={"name": "Compras"}).json()
    for text in ("C", "B", "A"):
        client.post(f"/api/lists/{lst['id']}/items", json={"text": text})
    c = lists(client)["Compras"]["items"][2]
    client.patch(f"/api/list-items/{c['id']}", json={"done": True})
    assert texts(client, "Compras") == ["A", "B", "C"]
    client.patch(f"/api/list-items/{c['id']}", json={"done": False})
    assert texts(client, "Compras") == ["C", "A", "B"]  # como lo muestra la pantalla al destachar


def test_item_to_skill(client: TestClient) -> None:
    learn = client.post("/api/lists", json={"name": "Quiero aprender", "for_learning": True}).json()
    item = client.post(f"/api/lists/{learn['id']}/items", json={"text": "Ajedrez"}).json()

    created = client.post(f"/api/list-items/{item['id']}/skill")
    assert created.status_code == 201
    skills = client.get("/api/skills", params={"today": "2026-10-14"}).json()
    assert [(s["id"], s["name"], s["stage"]) for s in skills] == [
        (created.json()["skill_id"], "Ajedrez", "practicando")
    ]
    assert lists(client)["Quiero aprender"]["items"][0]["done"] is True


def test_list_validation(client: TestClient) -> None:
    assert client.post("/api/lists", json={"name": ""}).status_code == 422
    assert client.post("/api/lists/nope/items", json={"text": "X"}).status_code == 404
    lst = client.post("/api/lists", json={"name": "X"}).json()
    assert client.post(f"/api/lists/{lst['id']}/items", json={"text": ""}).status_code == 422
    assert client.put("/api/list-items/nope/move", json={"position": 0}).status_code == 404
