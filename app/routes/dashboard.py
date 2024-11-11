from datetime import datetime, date
from decimal import Decimal
from http import HTTPStatus
from typing import Annotated, Literal

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, func

from app.config import Settings
from app.database import Transaction, User
from app.dependencies import get_current_user, get_session
from app.domain.value_objects.dashboard import FormatDashboardValues
from app.schemas.dashboard import DashboardResponse


dashboard_router = APIRouter(
    prefix="/dashboard",
    dependencies=[Depends(get_session), Depends(get_current_user)],
)

settings = Settings()  # type: ignore


def get_sum_of_type_of_transaction_by_interval(
    session,
    user_id: int,
    type_of_transaction: Literal["income", "expense"],
    start: date,
    end: date
) -> Decimal:

    total: Decimal | None = session.scalar(
        select(func.sum(Transaction.amount))
        .where(
            (Transaction.user_id == user_id)
            & (Transaction.type_of_transaction == type_of_transaction)
            & (Transaction.registration_date >= start)
            & (Transaction.registration_date <= end)
        )
    )
    return total or Decimal(0)


@dashboard_router.get(
    path="/",
    response_model=DashboardResponse,
    status_code=HTTPStatus.OK,
)
async def get_dashboard_resume(
    request: Request,
    month: Annotated[int | None, Query()] = None,
    year: Annotated[int | None, Query()] = None,
):
    current_user = request.state.user
    session = await get_session()
    db_user = session.scalar(select(User).where((User.username == current_user.sub)))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")

    current_date = date.today()
    query_params = dict(
        month=current_date.month,
        year=current_date.year,
    )
    if month:
        query_params["month"] = month
    if year:
        query_params["year"] = year

    month_start_date = datetime(year=query_params["year"], month=query_params["month"], day=1).date()
    month_end_date = month_start_date + relativedelta(months=1) - relativedelta(days=1)

    year_start_date = datetime.now().replace(month=1, day=1, year=query_params["year"]).date()
    year_end_date = datetime.now().replace(month=12, day=31, year=query_params["year"]).date()

    total_of_expenses_on_the_month = get_sum_of_type_of_transaction_by_interval(
        session=session,
        user_id=db_user.user_id,
        type_of_transaction="expense",
        start=month_start_date,
        end=month_end_date,
    )
    total_of_revenues_on_the_month = get_sum_of_type_of_transaction_by_interval(
        session=session,
        user_id=db_user.user_id,
        type_of_transaction="income",
        start=month_start_date,
        end=month_end_date,
    )

    total_of_expenses_on_the_year = get_sum_of_type_of_transaction_by_interval(
        session=session,
        user_id=db_user.user_id,
        type_of_transaction="expense",
        start=year_start_date,
        end=year_end_date,
    )
    total_of_revenues_on_the_year = get_sum_of_type_of_transaction_by_interval(
        session=session,
        user_id=db_user.user_id,
        type_of_transaction="income",
        start=year_start_date,
        end=year_end_date,
    )

    return DashboardResponse(
        monthlyRevenues=FormatDashboardValues.from_decimal_to_brl(
            total_of_revenues_on_the_month
        ),
        monthlyExpenses=FormatDashboardValues.from_decimal_to_brl(
            total_of_expenses_on_the_month
        ),
        yearlyRevenues=FormatDashboardValues.from_decimal_to_brl(
            total_of_revenues_on_the_year
        ),
        yearlyExpenses=FormatDashboardValues.from_decimal_to_brl(
            total_of_expenses_on_the_year
        ),
    )