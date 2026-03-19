from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.abstractions.repositories import (
    AbstractTransactionRepository,
    AbstractUserRepository,
)


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
            raise ValueError("User not found")
        
        return self.transaction_repo.delete(
            transaction_id=transaction_id,
        )
        
