from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import select

from app.config import Settings
from app.database import Transaction, User
from app.dependencies import get_current_user, get_session
from app.schemas.transactions import PaginatedTransactions, TransactionResponse


transactions_router = APIRouter(
    prefix="/transactions",
    dependencies=[Depends(get_session), Depends(get_current_user)]
)

settings = Settings() # type: ignore


def calculate_offset(page: int, items_per_page: int) -> int:
    return items_per_page * (page - 1)


def get_previous_and_next_pages(current_page: int) -> tuple[int | None, int | None]:
    previous = None
    if current_page > 1:
        previous = current_page - 1
    next_page = current_page + 1
    return previous, next_page



@transactions_router.get("/", response_model=PaginatedTransactions)
async def get_all_transactions(
    request: Request,
    items_per_page: Annotated[int | None, Query(alias="itemsPerPage")] = None,
    page: Annotated[int | None, Query(alias="page")] = None,
    previous: Annotated[int | None, Query(alias="prev")] = None,
    next_page: Annotated[int | None, Query(alias="next")] = None,
):
    current_user = await get_current_user(request=request)
    session = await get_session()
    db_user = session.scalar(
        select(User).where(
            (User.username == current_user.sub)
        )
    )
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="User not found"
        )
    
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
        items_per_page=query_params.get("itemsPerPage") or 10
    )
    
    transactions = session.scalars(
        select(Transaction).where(
            Transaction.user_id == db_user.user_id
        ).limit(limit).offset(offset)
    )

    previous_page, next_page = get_previous_and_next_pages(current_page=query_params.get("page") or 1)

    list_of_transactions_to_response_model = []
    for transaction in transactions:
        transaction_from_response = TransactionResponse(
            description=transaction.description,
            amount=TransactionResponse.format_to_currency(amount=transaction.amount),
            registration_date=TransactionResponse.format_date(date_reference=transaction.registration_date),
        )
        list_of_transactions_to_response_model.append(transaction_from_response)

    return PaginatedTransactions(
        page=query_params.get("page") or 1,
        prev=previous_page,
        next=next_page,
        items=list_of_transactions_to_response_model,
    )