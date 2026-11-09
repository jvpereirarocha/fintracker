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


@dataclass(frozen=True)
class MonthlyTotals:
    month: int
    income: Decimal
    expense: Decimal


@dataclass(frozen=True)
class MonthlySummary:
    year: int
    months: list[MonthlyTotals]


@dataclass(frozen=True)
class CategoryAmount:
    """Total spent in one category; category is None for uncategorized expenses"""

    category: str | None
    amount: Decimal


@dataclass(frozen=True)
class CategoryExpense:
    category: str
    amount: Decimal
    percentage: Decimal


@dataclass(frozen=True)
class ExpensesByCategory:
    month: int
    year: int
    total: Decimal
    categories: list[CategoryExpense]
