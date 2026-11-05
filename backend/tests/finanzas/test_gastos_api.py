from fastapi.testclient import TestClient


def test_expenses_by_month(client: TestClient) -> None:
    for day, amount in (("2026-10-01", 10), ("2026-10-31", 20), ("2026-11-01", 30)):
        client.post(
            "/api/finance/expenses", json={"date": day, "amount": amount, "category": "🍔 Comida"}
        )
    october = client.get("/api/finance/expenses", params={"month": "2026-10-10"}).json()
    assert [(e["date"], e["amount"]) for e in october] == [("2026-10-31", 20), ("2026-10-01", 10)]


def test_finance_validation(client: TestClient) -> None:
    expense = {"date": "2026-10-01", "amount": 10, "category": "🍔 Comida"}
    assert client.post("/api/finance/expenses", json={**expense, "amount": 0}).status_code == 422
    blank = {**expense, "category": "   "}
    assert client.post("/api/finance/expenses", json=blank).status_code == 422
    too_long = {"month": "2026-10-01", "amount": 5, "source": "x" * 31}
    assert client.post("/api/finance/income", json=too_long).status_code == 422
