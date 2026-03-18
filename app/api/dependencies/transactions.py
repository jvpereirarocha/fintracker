from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.base import get_db
from app.infra.repositories.categories import AdapterCategoryRepo
from app.infra.repositories.transactions import AdapterTransactionRepo
from app.infra.repositories.users import AdapterUserRepo
from app.usecases.transactions.create_transaction import CreateTransactionUseCase
from app.usecases.transactions.edit_transaction import UpdateTransactionUseCase
from app.usecases.transactions.list_transactions import ListTransactionsUseCase


async def get_list_transactions_use_case(
    db: Session = Depends(get_db)
) -> ListTransactionsUseCase:
    
    user_repo = AdapterUserRepo(session=db)
    transaction_repo = AdapterTransactionRepo(session=db)
    return ListTransactionsUseCase(user_repo=user_repo, transaction_repo=transaction_repo)


async def get_create_transaction_use_case(
    db: Session = Depends(get_db)
) -> CreateTransactionUseCase:
    user_repo = AdapterUserRepo(session=db)
    transaction_repo = AdapterTransactionRepo(session=db)
    category_repo = AdapterCategoryRepo(session=db)
    
    return CreateTransactionUseCase(
        user_repo=user_repo,
        transaction_repo=transaction_repo,
        category_repo=category_repo
    )


async def get_edit_transaction_use_case(
    db: Session = Depends(get_db)
) -> UpdateTransactionUseCase:
    user_repo = AdapterUserRepo(session=db)
    transaction_repo = AdapterTransactionRepo(session=db)
    category_repo = AdapterCategoryRepo(session=db)
    
    return UpdateTransactionUseCase(
        user_repo=user_repo,
        transaction_repo=transaction_repo,
        category_repo=category_repo
    )