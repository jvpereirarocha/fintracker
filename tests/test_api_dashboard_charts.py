from collections.abc import Iterator
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from app.api.dependencies.base import get_current_user
from app.api.dependencies.dashboards import (
    get_expenses_by_category_use_case,
    get_monthly_summary_use_case,
)
from app.domain.value_objects.dashboard import CategoryAmount, MonthlyTotals
from app.main import app
from app.usecases.dashboards.expenses_by_category import ExpensesByCategoryUseCase
from app.usecases.dashboards.monthly_summary import MonthlySummaryUseCase
from tests.fakes import FakeTransactionRepo, FakeUserRepo


def _logged_in_as_me(request: Request) -> SimpleNamespace:
    request.state.user = SimpleNamespace(sub="me")
    return request.state.user


@pytest.fixture
def client() -> Iterator[TestClient]:
    repo = FakeTransactionRepo(
        monthly_totals=[
            MonthlyTotals(month=3, income=Decimal("5000.00"), expense=Decimal("1200.50"))
        ],
        category_amounts=[
            CategoryAmount(category="Saúde", amount=Decimal("100.00")),
            CategoryAmount(category=None, amount=Decimal("300.00")),
        ],
    )
    app.dependency_overrides[get_current_user] = _logged_in_as_me
    app.dependency_overrides[get_monthly_summary_use_case] = lambda: MonthlySummaryUseCase(
        user_repo=FakeUserRepo(), transaction_repo=repo
    )
    app.dependency_overrides[get_expenses_by_category_use_case] = lambda: ExpensesByCategoryUseCase(
        user_repo=FakeUserRepo(), transaction_repo=repo
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_monthly_summary_returns_twelve_months_as_numbers(client: TestClient) -> None:
    response = client.get("/api/v1/dashboards/monthly", params={"year": 2024})

    assert response.status_code == 200
    body = response.json()
    assert body["year"] == 2024
    assert len(body["months"]) == 12
    assert body["months"][2] == {"month": 3, "income": 5000.0, "expense": 1200.5}
    assert body["months"][0] == {"month": 1, "income": 0.0, "expense": 0.0}


def test_expenses_by_category_returns_slices_as_numbers(client: TestClient) -> None:
    response = client.get(
        "/api/v1/dashboards/expenses-by-category", params={"month": 3, "year": 2025}
    )

    assert response.status_code == 200
    assert response.json() == {
        "month": 3,
        "year": 2025,
        "total": 400.0,
        "categories": [
            {"category": "Sem categoria", "amount": 300.0, "percentage": 75.0},
            {"category": "Saúde", "amount": 100.0, "percentage": 25.0},
        ],
    }


@pytest.mark.parametrize("month", [0, 13])
def test_expenses_by_category_rejects_month_out_of_range(client: TestClient, month: int) -> None:
    response = client.get(
        "/api/v1/dashboards/expenses-by-category", params={"month": month, "year": 2025}
    )

    assert response.status_code == 422
