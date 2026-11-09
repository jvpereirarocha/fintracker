from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, PlainSerializer, field_serializer

from app.domain.business_logic.conversor import format_decimal_to_brl_format


class DashboardResponse(BaseModel):
    monthly_revenues: Decimal = Field(serialization_alias="monthlyRevenues")
    monthly_expenses: Decimal = Field(serialization_alias="monthlyExpenses")
    monthly_balance: Decimal = Field(serialization_alias="monthlyBalance")
    yearly_revenues: Decimal = Field(serialization_alias="yearlyRevenues")
    yearly_expenses: Decimal = Field(serialization_alias="yearlyExpenses")
    yearly_balance: Decimal = Field(serialization_alias="yearlyBalance")

    @field_serializer("monthly_revenues")
    def serialize_monthly_revenues(self, amount: Decimal) -> str:
        return format_decimal_to_brl_format(amount=amount)

    @field_serializer("monthly_expenses")
    def serialize_monthly_expenses(self, amount: Decimal) -> str:
        return format_decimal_to_brl_format(amount=amount)

    @field_serializer("monthly_balance")
    def serialize_monthly_balance(self, amount: Decimal) -> str:
        return format_decimal_to_brl_format(amount=amount)

    @field_serializer("yearly_revenues")
    def serialize_yearly_revenues(self, amount: Decimal) -> str:
        return format_decimal_to_brl_format(amount=amount)

    @field_serializer("yearly_expenses")
    def serialize_yearly_expenses(self, amount: Decimal) -> str:
        return format_decimal_to_brl_format(amount=amount)

    @field_serializer("yearly_balance")
    def serialize_yearly_balance(self, amount: Decimal) -> str:
        return format_decimal_to_brl_format(amount=amount)


# Chart payloads send money as plain numbers; the frontend formats them as R$
Money = Annotated[Decimal, PlainSerializer(float, return_type=float)]


class MonthlyTotalsResponse(BaseModel):
    month: int
    income: Money
    expense: Money


class MonthlySummaryResponse(BaseModel):
    year: int
    months: list[MonthlyTotalsResponse]


class CategoryExpenseResponse(BaseModel):
    category: str
    amount: Money
    percentage: Money


class ExpensesByCategoryResponse(BaseModel):
    month: int
    year: int
    total: Money
    categories: list[CategoryExpenseResponse]
