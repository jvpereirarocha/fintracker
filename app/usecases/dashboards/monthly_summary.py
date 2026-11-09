from datetime import date
from decimal import Decimal

from app.domain.abstractions.repositories import (
    AbstractTransactionRepository,
    AbstractUserRepository,
)
from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.exceptions.users import UserNotFoundException
from app.domain.value_objects.dashboard import MonthlySummary, MonthlyTotals


class MonthlySummaryUseCase(AbstractUseCase):
    """Income and expense of each of the 12 months of a year, by registration date"""

    def __init__(
        self,
        user_repo: AbstractUserRepository,
        transaction_repo: AbstractTransactionRepository,
    ) -> None:
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo

    async def execute(self, username: str, year: int | None = None) -> MonthlySummary:
        user_id = self.user_repo.get_user_id_by_username(username=username)
        if not user_id:
            raise UserNotFoundException(f"User {username} not found")
        year = year or date.today().year

        totals_by_month = {
            totals.month: totals
            for totals in self.transaction_repo.get_monthly_totals_by_year(
                user_id=user_id, year=year
            )
        }
        months = [
            totals_by_month.get(
                month, MonthlyTotals(month=month, income=Decimal(0), expense=Decimal(0))
            )
            for month in range(1, 13)
        ]
        return MonthlySummary(year=year, months=months)
