from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class DashboardValues:
    total_expense: Decimal
    total_income: Decimal


@dataclass(frozen=True)
class DashboardResume:
    monthly_revenues: Decimal
    monthly_expenses: Decimal
    yearly_revenues: Decimal
    yearly_expenses: Decimal

    @property
    def monthly_balance(self) -> Decimal:
        return Decimal(self.monthly_revenues - self.monthly_expenses)

    @property
    def yearly_balance(self) -> Decimal:
        return Decimal(self.yearly_revenues - self.yearly_expenses)
