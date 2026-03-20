from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.abstractions.repositories import (
    AbstractTransactionRepository,
    AbstractUserRepository,
)
from app.domain.exceptions.transactions import TransactionNotFoundException
from app.domain.exceptions.users import UserNotFoundException


class DeleteTransactionUseCase(AbstractUseCase):
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        transaction_repo: AbstractTransactionRepository,
    ):
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo


    async def execute(
        self,
        transaction_id: int,
        username: str,
    ) -> None:
        
        user_id = self.user_repo.get_user_id_by_username(username=username)
        if not user_id:
            raise UserNotFoundException(f"User {username} not found")
        
        transaction = self.transaction_repo.fetch_one(transaction_id=transaction_id)
        if not transaction:
            raise TransactionNotFoundException(f"Transaction with id {transaction_id} not found")
        
        return self.transaction_repo.delete(
            transaction_id=transaction_id,
        )
        
