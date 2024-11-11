from pydantic import Field, BaseModel


class DashboardResponse(BaseModel):
    monthly_revenues: str = Field(alias="monthlyRevenues")
    monthly_expenses: str = Field(alias="monthlyExpenses")
    yearly_revenues: str = Field(alias="yearlyRevenues")
    yearly_expenses: str = Field(alias="yearlyExpenses")