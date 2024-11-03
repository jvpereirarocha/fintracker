from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select

from app.config import Settings
from app.database import Transaction, User
from app.dependencies import get_current_user, get_session
from app.schemas.transactions import (
    PaginatedTransactions,
    TransactionResponse,
    PersistTransaction,
    NonRequiredPersistTransaction,
    DeletedTransaction,
)

transactions_router = APIRouter(
    prefix="/transactions",
    dependencies=[Depends(get_session), Depends(get_current_user)],
)

settings = Settings()  # type: ignore


def calculate_offset(page: int, items_per_page: int) -> int:
    return items_per_page * (page - 1)


def calculate_total_of_pages(total_of_items: int, items_per_page: int) -> int:
    total_of_pages = (total_of_items + items_per_page - 1) // items_per_page
    if total_of_pages < 1:
        return 1
    return total_of_pages


def get_previous_page(current_page: int) -> int | None:
    if current_page == 1:
        return None

    return current_page - 1


def get_next_page(current_page: int, total_of_pages: int) -> int | None:
    if current_page < total_of_pages:
        return current_page + 1

    return None


@transactions_router.get(
    path="/",
    response_model=PaginatedTransactions,
    status_code=HTTPStatus.OK,
)
async def get_all_transactions(
    request: Request,
    items_per_page: Annotated[int | None, Query(alias="itemsPerPage")] = None,
    page: Annotated[int | None, Query(alias="page")] = None,
    previous: Annotated[int | None, Query(alias="prev")] = None,
    next_page: Annotated[int | None, Query(alias="next")] = None,
):
    current_user = request.state.user
    session = await get_session()
    db_user = session.scalar(select(User).where((User.username == current_user.sub)))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")

    query_params: dict[str, int | None] = {}
    if items_per_page:
        query_params.update({"itemsPerPage": items_per_page})
    if page:
        query_params.update({"page": page})
    if previous:
        query_params.update({"prev": previous})
    if next_page:
        query_params.update({"next": next_page})

    limit = query_params.get("itemsPerPage") or 10
    offset = calculate_offset(
        page=query_params.get("page") or 1,
        items_per_page=query_params.get("itemsPerPage") or 10,
    )

    transactions = session.scalars(
        select(Transaction)
        .where(Transaction.user_id == db_user.user_id)
        .limit(limit)
        .offset(offset)
    )

    total_of_transactions = (
        session.query(Transaction).where(Transaction.user_id == db_user.user_id).count()
    )

    total_of_pages = calculate_total_of_pages(
        total_of_items=total_of_transactions, items_per_page=limit
    )

    previous_page = get_previous_page(current_page=query_params.get("page") or 1)
    next_page = get_next_page(
        current_page=query_params.get("page") or 1, total_of_pages=total_of_pages
    )

    list_of_transactions_to_response_model = []
    for transaction in transactions:
        transaction_from_response = TransactionResponse(
            description=transaction.description,
            amount=TransactionResponse.format_to_currency(amount=transaction.amount),
            registration_date=TransactionResponse.format_date(
                date_reference=transaction.registration_date
            ),
        )
        list_of_transactions_to_response_model.append(transaction_from_response)

    return PaginatedTransactions(
        items_per_page=limit,
        total_of_pages=total_of_pages,
        page=query_params.get("page") or 1,
        prev=previous_page,
        next=next_page,
        items=list_of_transactions_to_response_model,
    )


@transactions_router.get(
    path="/{transaction_id}",
    response_model=TransactionResponse,
    status_code=HTTPStatus.OK,
)
async def detail_transaction(
    request: Request,
    transaction_id: int,
):
    current_user = request.state.user
    session = await get_session()
    db_user = session.scalar(select(User).where((User.username == current_user.sub)))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")

    transaction = session.scalar(
        select(Transaction).where(
            (Transaction.transaction_id == transaction_id)
            & (Transaction.user_id == db_user.user_id)
        )
    )
    if not transaction:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Transaction not found"
        )

    return TransactionResponse(
        description=transaction.description,
        amount=TransactionResponse.format_to_currency(amount=transaction.amount),
        registration_date=TransactionResponse.format_date(
            date_reference=transaction.registration_date
        ),
    )


@transactions_router.post(
    path="/",
    response_model=TransactionResponse,
    status_code=HTTPStatus.CREATED,
)
async def create_transaction(request: Request, transaction_dto: PersistTransaction):
    current_user = request.state.user
    session = await get_session()
    db_user = session.scalar(select(User).where((User.username == current_user.sub)))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")

    transaction = Transaction(
        description=transaction_dto.description,
        amount=transaction_dto.amount,
        type_of_transaction=transaction_dto.type_of_transaction,
        registration_date=transaction_dto.registration_date,
        user_id=db_user.user_id,
    )
    session.add(transaction)
    session.commit()

    return TransactionResponse(
        description=transaction.description,
        amount=TransactionResponse.format_to_currency(amount=transaction.amount),
        registration_date=TransactionResponse.format_date(
            date_reference=transaction.registration_date
        ),
    )


@transactions_router.put(
    path="/{transaction_id}",
    response_model=TransactionResponse,
    status_code=HTTPStatus.OK,
)
async def update_transaction(
    request: Request, transaction_id: int, transaction_dto: PersistTransaction
):
    current_user = request.state.user
    session = await get_session()
    db_user = session.scalar(select(User).where((User.username == current_user.sub)))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")

    transaction = session.scalar(
        select(Transaction).where(
            (Transaction.transaction_id == transaction_id)
            & (Transaction.user_id == db_user.user_id)
        )
    )
    if not transaction:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Transaction not found"
        )

    transaction.description = transaction_dto.description
    transaction.amount = transaction_dto.amount
    transaction.type_of_transaction = transaction_dto.type_of_transaction
    transaction.registration_date = transaction_dto.registration_date

    session.add(transaction)
    session.commit()

    return TransactionResponse(
        description=transaction.description,
        amount=TransactionResponse.format_to_currency(amount=transaction.amount),
        registration_date=TransactionResponse.format_date(
            date_reference=transaction.registration_date
        ),
    )


@transactions_router.patch(
    path="/{transaction_id}",
    response_model=TransactionResponse,
    status_code=HTTPStatus.OK,
)
async def partial_update_transaction(
    request: Request,
    transaction_id: int,
    transaction_dto: NonRequiredPersistTransaction,
):
    current_user = request.state.user
    session = await get_session()
    db_user = session.scalar(select(User).where((User.username == current_user.sub)))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")

    transaction = session.scalar(
        select(Transaction).where(
            (Transaction.transaction_id == transaction_id)
            & (Transaction.user_id == db_user.user_id)
        )
    )
    if not transaction:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Transaction not found"
        )

    transaction.description = transaction_dto.description or transaction.description
    transaction.amount = transaction_dto.amount or transaction.amount
    transaction.type_of_transaction = (
        transaction_dto.type_of_transaction or transaction.type_of_transaction
    )
    transaction.registration_date = (
        transaction_dto.registration_date or transaction.registration_date
    )

    session.add(transaction)
    session.commit()

    return TransactionResponse(
        description=transaction.description,
        amount=TransactionResponse.format_to_currency(amount=transaction.amount),
        registration_date=TransactionResponse.format_date(
            date_reference=transaction.registration_date
        ),
    )


@transactions_router.delete(
    "/{transaction_id}", response_model=TransactionResponse, status_code=HTTPStatus.OK
)
async def delete_transaction(
    request: Request,
    transaction_id: int,
):
    current_user = request.state.user
    session = await get_session()
    db_user = session.scalar(select(User).where((User.username == current_user.sub)))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")

    transaction = session.scalar(
        select(Transaction).where(
            (Transaction.transaction_id == transaction_id)
            & (Transaction.user_id == db_user.user_id)
        )
    )
    if not transaction:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Transaction not found"
        )

    session.delete(transaction)
    session.commit()

    return DeletedTransaction(message="Transaction was deleted successfully")
