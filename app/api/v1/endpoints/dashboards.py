from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies.base import get_current_user
from app.api.dependencies.dashboards import get_dashboard_resume_use_case
from app.api.v1.dtos.dashboard import DashboardResponse
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
