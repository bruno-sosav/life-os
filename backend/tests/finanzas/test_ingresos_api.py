from fastapi.testclient import TestClient


def test_income_by_month(client: TestClient) -> None:
    created = client.post(
        "/api/finance/income", json={"month": "2026-10-15", "amount": 1500.5, "source": "Sueldo"}
    ).json()
    assert (created["month"], created["amount"]) == ("2026-10-01", 1500.5)
    client.post("/api/finance/income", json={"month": "2026-11-01", "amount": 100})

    october = client.get("/api/finance/income", params={"month": "2026-10-31"}).json()
    assert [i["amount"] for i in october] == [1500.5]

    client.delete(f"/api/finance/income/{created['id']}")
    assert client.get("/api/finance/income", params={"month": "2026-10-01"}).json() == []
