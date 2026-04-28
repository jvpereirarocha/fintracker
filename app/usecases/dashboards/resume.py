from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from app.domain.abstractions.repositories import (
    AbstractTransactionRepository,
    AbstractUserRepository,
)
from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.exceptions.users import UserNotFoundException
from app.domain.value_objects.dashboard import DashboardResume


class DashboardResumeUseCase(AbstractUseCase):
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        transaction_repo: AbstractTransactionRepository,
    ) -> None:
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo

    @classmethod
    def get_month_and_year_by_params(cls, month: int | None, year: int | None) -> tuple[int, int]:
        current_date = date.today()
        current_month = current_date.month
        current_year = current_date.year

        if month:
            current_month = month
        if year:
            current_year = year

        return current_month, current_year

    @classmethod
    def get_monthly_interval_by_month_and_year(cls, month: int, year: int) -> tuple[date, date]:
        first_day_of_month: date = datetime(year=year, month=month, day=1).date()
        last_day_of_month: date = (
            first_day_of_month + relativedelta(months=1) - relativedelta(days=1)
        )
        return first_day_of_month, last_day_of_month

    @classmethod
    def get_yearly_interval_year(cls, year: int) -> tuple[date, date]:
        first_day_of_year: date = date(year=year, month=1, day=1)
        last_day_of_year: date = date(year=year, month=12, day=31)
        return first_day_of_year, last_day_of_year

    async def execute(
        self,
        username: str,
        month: int | None = None,
        year: int | None = None,
    ) -> DashboardResume:
        user_id = self.user_repo.get_user_id_by_username(username=username)
        if not user_id:
            raise UserNotFoundException(f"User {username} not found")
        month, year = self.get_month_and_year_by_params(month=month, year=year)
        first_day_of_month, last_day_of_month = self.get_monthly_interval_by_month_and_year(
            month=month, year=year
        )
        first_day_of_year, last_day_of_year = self.get_yearly_interval_year(year=year)
        month_dashboard_resume = self.transaction_repo.get_sum_of_transactions_by_interval(
            user_id=user_id,
            start_date=first_day_of_month,
            end_date=last_day_of_month,
        )
        year_dashboard_resume = self.transaction_repo.get_sum_of_transactions_by_interval(
            user_id=user_id,
            start_date=first_day_of_year,
            end_date=last_day_of_year,
        )
        return DashboardResume(
            monthly_revenues=month_dashboard_resume.total_income,
            monthly_expenses=month_dashboard_resume.total_expense,
            yearly_revenues=year_dashboard_resume.total_income,
            yearly_expenses=year_dashboard_resume.total_expense,
        )
