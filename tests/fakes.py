from datetime import date
from typing import Any

from app.domain.abstractions.repositories import (
    AbstractTransactionRepository,
    AbstractUserRepository,
)
from app.domain.value_objects.dashboard import CategoryAmount, MonthlyTotals


class FakeUserRepo(AbstractUserRepository):
    def __init__(self, user_id: int | None = 1) -> None:
        self.user_id = user_id

    def get_user_id_by_username(self, username: str) -> int | None:
        return self.user_id


class FakeTransactionRepo(AbstractTransactionRepository):
    def __init__(
        self,
        monthly_totals: list[MonthlyTotals] | None = None,
        category_amounts: list[CategoryAmount] | None = None,
    ) -> None:
        self.monthly_totals = monthly_totals or []
        self.category_amounts = category_amounts or []
        self.calls: list[dict[str, Any]] = []

    def get_monthly_totals_by_year(self, user_id: int, year: int) -> list[MonthlyTotals]:
        self.calls.append({"user_id": user_id, "year": year})
        return self.monthly_totals

    def get_expenses_by_category(
        self, user_id: int, start_date: date, end_date: date
    ) -> list[CategoryAmount]:
        self.calls.append({"user_id": user_id, "start_date": start_date, "end_date": end_date})
        return self.category_amounts
