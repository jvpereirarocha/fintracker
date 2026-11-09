from decimal import Decimal

from app.domain.abstractions.repositories import (
    AbstractTransactionRepository,
    AbstractUserRepository,
)
from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.business_logic.dashboard import compute_percentages
from app.domain.exceptions.users import UserNotFoundException
from app.domain.value_objects.dashboard import CategoryExpense, ExpensesByCategory
from app.usecases.dashboards.resume import DashboardResumeUseCase

UNCATEGORIZED_LABEL = "Sem categoria"


class ExpensesByCategoryUseCase(AbstractUseCase):
    """Share of the month's expenses spent in each category, by registration date"""

    def __init__(
        self,
        user_repo: AbstractUserRepository,
        transaction_repo: AbstractTransactionRepository,
    ) -> None:
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo

    async def execute(
        self,
        username: str,
        month: int | None = None,
        year: int | None = None,
    ) -> ExpensesByCategory:
        user_id = self.user_repo.get_user_id_by_username(username=username)
        if not user_id:
            raise UserNotFoundException(f"User {username} not found")
        month, year = DashboardResumeUseCase.get_month_and_year_by_params(month=month, year=year)
        start_date, end_date = DashboardResumeUseCase.get_monthly_interval_by_month_and_year(
            month=month, year=year
        )

        amounts = sorted(
            self.transaction_repo.get_expenses_by_category(
                user_id=user_id, start_date=start_date, end_date=end_date
            ),
            key=lambda item: item.amount,
            reverse=True,
        )
        percentages = compute_percentages([item.amount for item in amounts])
        categories = [
            CategoryExpense(
                category=item.category or UNCATEGORIZED_LABEL,
                amount=item.amount,
                percentage=percentage,
            )
            for item, percentage in zip(amounts, percentages, strict=True)
        ]
        return ExpensesByCategory(
            month=month,
            year=year,
            total=sum((item.amount for item in amounts), Decimal(0)),
            categories=categories,
        )
