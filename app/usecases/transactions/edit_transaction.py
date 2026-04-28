from app.domain.abstractions.repositories import (
    AbstractCategoryRepository,
    AbstractTransactionRepository,
    AbstractUserRepository,
)
from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.entities.transactions import SaveTransaction, TransactionEntity
from app.domain.exceptions.categories import CategoryNotFoundException
from app.domain.exceptions.users import UserNotFoundException


class UpdateTransactionUseCase(AbstractUseCase):
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        transaction_repo: AbstractTransactionRepository,
        category_repo: AbstractCategoryRepository,
    ):
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo

    async def execute(
        self,
        transaction_id: int,
        edit_transaction: SaveTransaction,
        username: str,
    ) -> TransactionEntity:
        user_id = self.user_repo.get_user_id_by_username(username=username)
        if not user_id:
            raise UserNotFoundException(f"User {username} not found")

        category_id = self.category_repo.get_category_id_by_name(name=edit_transaction.category)
        if not category_id:
            raise CategoryNotFoundException(f"Category {edit_transaction.category} not found")

        return self.transaction_repo.update(
            transaction_id=transaction_id,
            edit_transaction=edit_transaction,
            category_id=category_id,
        )
