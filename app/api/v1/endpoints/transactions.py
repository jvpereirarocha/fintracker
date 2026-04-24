from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies.transactions import (
    get_create_transaction_use_case,
    get_edit_transaction_use_case,
    get_list_transactions_use_case,
    get_delete_transaction_use_case,
    get_one_transactions_use_case,
)
from app.api.v1.dtos.transactions import (
    SaveTransactionRequestDTO,
    PaginatedTransactions,
    TransactionResponse
)
from app.api.dependencies.base import get_current_user
from app.domain.entities.transactions import SaveTransaction
from app.domain.value_objects.transactions import TransactionsFilter
from app.usecases.transactions.create_transaction import CreateTransactionUseCase
from app.usecases.transactions.edit_transaction import UpdateTransactionUseCase
from app.usecases.transactions.list_transactions import ListTransactionsUseCase, GetOneTransactionUseCase
from app.usecases.transactions.delete_transaction import DeleteTransactionUseCase


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
    status_of_transaction: Annotated[str | None, Query(alias="status")] = None,
    items_per_page: Annotated[int, Query(alias="itemsPerPage")] = 10,
    page: Annotated[int, Query(alias="page")] = 1,
    use_case: ListTransactionsUseCase = Depends(get_list_transactions_use_case)
):
    current_user = request.state.user

    filters = TransactionsFilter(
        username=current_user.sub,
        month=month,
        year=year,
        description=description,
        category=category,
        type_of_transaction=type_of_transaction, # type: ignore
        status_of_transaction=status_of_transaction, # type: ignore
    )

    return await use_case.execute(
        filters=filters,
        page=page,
        page_size=items_per_page,
    )


@transactions_router.get(
    path="/{transaction_id}",
    response_model=TransactionResponse,
    status_code=HTTPStatus.OK,
)
async def fetch_one_transaction(
    request: Request,
    transaction_id: int,
    use_case: GetOneTransactionUseCase = Depends(get_one_transactions_use_case)
):
    current_user = request.state.user

    return await use_case.execute(
        transaction_id=transaction_id,
        username=current_user.sub,
    )


@transactions_router.post(
    path="/",
    response_model=TransactionResponse,
    status_code=HTTPStatus.CREATED,
)
async def create_transaction(
    request: Request,
    payload: SaveTransactionRequestDTO,
    use_case: CreateTransactionUseCase = Depends(get_create_transaction_use_case)
):
    current_user = request.state.user
    new_transaction = SaveTransaction(
        description=payload.description,
        amount=payload.amount,
        type_of_transaction=payload.type_of_transaction,
        registration_date=payload.registration_date,
        due_date=payload.due_date,
        category=payload.category,
        transaction_status=payload.transaction_status,
    )
    
    return await use_case.execute(
        new_transaction=new_transaction,
        username=current_user.sub,
    )


@transactions_router.put(
    path="/{transaction_id}",
    response_model=TransactionResponse,
    status_code=HTTPStatus.OK,
)
async def update_transaction(
    request: Request,
    transaction_id: int,
    payload: SaveTransactionRequestDTO,
    use_case: UpdateTransactionUseCase = Depends(get_edit_transaction_use_case)
):
    current_user = request.state.user
    edit_transaction = SaveTransaction(
        description=payload.description,
        amount=payload.amount,
        type_of_transaction=payload.type_of_transaction,
        registration_date=payload.registration_date,
        due_date=payload.due_date,
        category=payload.category,
        transaction_status=payload.transaction_status,
    )
    
    return await use_case.execute(
        transaction_id=transaction_id,
        edit_transaction=edit_transaction,
        username=current_user.sub,

    )


@transactions_router.delete(
    path="/{transaction_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_transaction(
    request: Request,
    transaction_id: int,
    use_case: DeleteTransactionUseCase = Depends(get_delete_transaction_use_case)
):
    current_user = request.state.user
    
    return await use_case.execute(
        transaction_id=transaction_id,
        username=current_user.sub,
    )