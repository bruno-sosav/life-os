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


def test_month_summary(client: TestClient) -> None:
    def summary() -> dict[str, object]:
        data: dict[str, object] = client.get(
            "/api/finance/summary", params={"month": "2026-10-20"}
        ).json()
        return data

    empty = summary()
    assert (empty["month"], empty["income"], empty["savings_pct"]) == ("2026-10-01", 0.0, None)
    assert empty["spent_pct"] is None and empty["by_category"] == []

    client.post("/api/finance/income", json={"month": "2026-10-01", "amount": 1000})
    for day, amount, category in (
        ("2026-10-02", 150, "🍔 Comida"),
        ("2026-10-03", 50, "🍔 Comida"),
        ("2026-10-04", 50, "🎬 Cine"),
        ("2026-11-01", 999, "🍔 Comida"),  # otro mes
    ):
        client.post(
            "/api/finance/expenses", json={"date": day, "amount": amount, "category": category}
        )
    result = summary()
    assert (result["income"], result["expenses"], result["savings"]) == (1000.0, 250.0, 750.0)
    assert (result["savings_pct"], result["spent_pct"]) == (75, 25)
    assert result["by_category"] == [
        {"category": "🍔 Comida", "total": 200.0, "pct": 80.0},
        {"category": "🎬 Cine", "total": 50.0, "pct": 20.0},
    ]


def test_overspending_caps_spent_pct(client: TestClient) -> None:
    client.post("/api/finance/income", json={"month": "2026-10-01", "amount": 100})
    client.post(
        "/api/finance/expenses", json={"date": "2026-10-02", "amount": 300, "category": "X"}
    )
    result = client.get("/api/finance/summary", params={"month": "2026-10-01"}).json()
    assert (result["savings"], result["savings_pct"], result["spent_pct"]) == (-200.0, -200, 100)


def test_labels_in_use(client: TestClient) -> None:
    for category in ("🎬 Cine", "🍔 Comida", "🍔 Comida"):
        client.post(
            "/api/finance/expenses", json={"date": "2026-10-02", "amount": 1, "category": category}
        )
    client.post(
        "/api/finance/income", json={"month": "2026-10-01", "amount": 1, "source": "Sueldo"}
    )
    client.post("/api/finance/income", json={"month": "2026-10-01", "amount": 1})  # sin fuente
    assert client.get("/api/finance/labels").json() == {
        "expense_categories": ["🍔 Comida", "🎬 Cine"],
        "income_sources": ["Sueldo"],
    }
