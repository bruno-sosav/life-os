from fastapi.testclient import TestClient


def test_income_by_month(client: TestClient) -> None:
    created = client.post(
        "/api/finance/income", json={"month": "2026-10-15", "amount": 1500.5, "source": "sueldo"}
    ).json()
    assert (created["month"], created["amount"]) == ("2026-10-01", 1500.5)
    client.post("/api/finance/income", json={"month": "2026-11-01", "amount": 100})

    october = client.get("/api/finance/income", params={"month": "2026-10-31"}).json()
    assert [i["amount"] for i in october] == [1500.5]

    client.delete(f"/api/finance/income/{created['id']}")
    assert client.get("/api/finance/income", params={"month": "2026-10-01"}).json() == []


def test_expenses_by_month(client: TestClient) -> None:
    for day, amount in (("2026-10-01", 10), ("2026-10-31", 20), ("2026-11-01", 30)):
        client.post(
            "/api/finance/expenses", json={"date": day, "amount": amount, "category": "comida"}
        )
    october = client.get("/api/finance/expenses", params={"month": "2026-10-10"}).json()
    assert [(e["date"], e["amount"]) for e in october] == [("2026-10-31", 20), ("2026-10-01", 10)]


def test_finance_validation(client: TestClient) -> None:
    expense = {"date": "2026-10-01", "amount": 10, "category": "comida"}
    assert client.post("/api/finance/expenses", json={**expense, "amount": 0}).status_code == 422
    bad_category = {**expense, "category": "casino"}
    assert client.post("/api/finance/expenses", json=bad_category).status_code == 422
    bad_source = {"month": "2026-10-01", "amount": 5, "source": "lotería"}
    assert client.post("/api/finance/income", json=bad_source).status_code == 422
