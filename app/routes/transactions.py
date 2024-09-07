from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select

from app.config import Settings
from app.database import Transaction, User
from app.dependencies import get_current_user, get_session
from app.schemas.transactions import TransactionResponse


transactions_router = APIRouter(
    prefix="/transactions",
    dependencies=[Depends(get_session), Depends(get_current_user)]
)

settings = Settings() # type: ignore


class TransactionTest(BaseModel):
    message: str

@transactions_router.get("/", response_model=list[TransactionResponse])
async def get_all_transactions(request: Request):
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
    
    transactions = session.scalars(
        select(Transaction).where(
            Transaction.user_id == db_user.user_id
        )
    )

    list_of_transactions_to_response_model = []
    for transaction in transactions:
        transaction_from_response = TransactionResponse(transaction)
        list_of_transactions_to_response_model.append(transaction_from_response)

    return list_of_transactions_to_response_model