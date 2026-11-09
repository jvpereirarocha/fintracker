from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies.base import get_current_user
from app.api.dependencies.dashboards import (
    get_dashboard_resume_use_case,
    get_expenses_by_category_use_case,
    get_monthly_summary_use_case,
)
from app.api.v1.dtos.dashboard import (
    DashboardResponse,
    ExpensesByCategoryResponse,
    MonthlySummaryResponse,
)
from app.domain.value_objects.dashboard import ExpensesByCategory, MonthlySummary
from app.usecases.dashboards.expenses_by_category import ExpensesByCategoryUseCase
from app.usecases.dashboards.monthly_summary import MonthlySummaryUseCase
from app.usecases.dashboards.resume import DashboardResumeUseCase

dashboard_router = APIRouter(
    prefix="/dashboards",
    dependencies=[Depends(get_current_user)],
)


@dashboard_router.get(
    path="/",
    response_model=DashboardResponse,
    status_code=HTTPStatus.OK,
)
async def get_dashboard_resume(
    request: Request,
    month: Annotated[int | None, Query()] = None,
    year: Annotated[int | None, Query()] = None,
    use_case: DashboardResumeUseCase = Depends(get_dashboard_resume_use_case),
):
    current_user = request.state.user
    return await use_case.execute(username=current_user.sub, month=month, year=year)


@dashboard_router.get(
    path="/monthly",
    response_model=MonthlySummaryResponse,
    status_code=HTTPStatus.OK,
)
async def get_monthly_summary(
    request: Request,
    year: Annotated[int | None, Query(ge=1, le=9999)] = None,
    use_case: MonthlySummaryUseCase = Depends(get_monthly_summary_use_case),
) -> MonthlySummary:
    """Income and expense of each month of the year (bar and line charts)"""
    current_user = request.state.user
    return await use_case.execute(username=current_user.sub, year=year)


@dashboard_router.get(
    path="/expenses-by-category",
    response_model=ExpensesByCategoryResponse,
    status_code=HTTPStatus.OK,
)
async def get_expenses_by_category(
    request: Request,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    year: Annotated[int | None, Query(ge=1, le=9999)] = None,
    use_case: ExpensesByCategoryUseCase = Depends(get_expenses_by_category_use_case),
) -> ExpensesByCategory:
    """Share of the month's expenses per category (pie chart)"""
    current_user = request.state.user
    return await use_case.execute(username=current_user.sub, month=month, year=year)
