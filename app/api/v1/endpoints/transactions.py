from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies.transactions import get_list_transactions_use_case
from app.api.v1.dtos.transactions import PaginatedTransactions
from app.dependencies import get_current_user
from app.domain.value_objects.transactions import TransactionsFilter
from app.usecases.transactions.list_transactions import ListTransactionsUseCase


transactions_router = APIRouter(
    prefix="/transactions",
    dependencies=[Depends(get_current_user)],
)


@transactions_router.get(
    path="/",
    response_model=PaginatedTransactions,
    status_code=HTTPStatus.OK,
)
async def get_all_transactions(
    request: Request,
    month: Annotated[int | None, Query(alias="month")] = None,
    year: Annotated[int | None, Query(alias="year")] = None,
    description: Annotated[str | None, Query(alias="description")] = None,
    category: Annotated[str | None, Query(alias="category")] = None,
    type_of_transaction: Annotated[str | None, Query(alias="typeOfTransaction")] = None,
    items_per_page: Annotated[int | None, Query(alias="itemsPerPage")] = None,
    page: Annotated[int | None, Query(alias="page")] = None,
    use_case: ListTransactionsUseCase = Depends(get_list_transactions_use_case)
):
    current_user = request.state.user

    filters = TransactionsFilter(
        username=current_user.sub,
        month=month,
        year=year,
        description=description,
        category=category,
        type_of_transaction=type_of_transaction
    )

    return await use_case.execute(
        filters=filters,
        page=page,
        page_size=items_per_page,
    )