from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.base import get_db
from app.infra.repositories.transactions import SqlTransactionRepo
from app.usecases.transactions.list_transactions import ListTransactionsUseCase


async def get_list_transactions_use_case(
    db: Session = Depends(get_db)
) -> ListTransactionsUseCase:
    
    repo = SqlTransactionRepo(session=db)
    return ListTransactionsUseCase(repo=repo)