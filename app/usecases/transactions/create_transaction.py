from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.abstractions.repositories import (
    AbstractTransactionRepository,
    AbstractUserRepository,
    AbstractCategoryRepository,
)
from app.domain.entities.transactions import NewTransaction, TransactionEntity


class CreateTransactionUseCase(AbstractUseCase):
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        transaction_repo: AbstractTransactionRepository,
        category_repo: AbstractCategoryRepository
    ):
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo


    async def execute(
        self,
        new_transaction: NewTransaction,
        username: str,
    ) -> TransactionEntity:
        
        user_id = self.user_repo.get_user_id_by_username(username=username)
        if not user_id:
            raise ValueError("User not found")
        
        category_id = self.category_repo.get_category_id_by_name(name=new_transaction.category)
        if not category_id:
            raise ValueError("Category not found")
        
        return self.transaction_repo.save(
            new_transaction=new_transaction,
            user_id=user_id,
            category_id=category_id
        )
        
