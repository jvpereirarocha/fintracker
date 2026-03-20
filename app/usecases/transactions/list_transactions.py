from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.abstractions.repositories import AbstractTransactionRepository, AbstractUserRepository
from app.domain.exceptions.transactions import TransactionNotFoundException
from app.domain.exceptions.users import UserNotFoundException
from app.domain.value_objects.transactions import TransactionsFilter
from app.domain.entities.base import PagedResponse
from app.domain.entities.transactions import TransactionEntity


class ListTransactionsUseCase(AbstractUseCase):
    def __init__(self, user_repo: AbstractUserRepository, transaction_repo: AbstractTransactionRepository):
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo

    async def execute(
        self,
        filters: TransactionsFilter,
        page: int,
        page_size: int
    ) -> PagedResponse[TransactionEntity]:
        
        user_id = self.user_repo.get_user_id_by_username(username=filters.username)
        if not user_id:
            raise UserNotFoundException(f"User {filters.username} not found")
        
        items, total = self.transaction_repo.fetch_all(
            user_id=user_id,
            filters=filters,
            page=page,
            page_size=page_size,
        )

        return PagedResponse(
            items=items,
            total_count=total,
            page=page,
            items_per_page=page_size
        )
    

class GetOneTransactionUseCase(AbstractUseCase):
    def __init__(self, user_repo: AbstractUserRepository, transaction_repo: AbstractTransactionRepository):
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo

    async def execute(
        self,
        transaction_id: int,
        username: str,
    ) -> TransactionEntity:
        
        user_id = self.user_repo.get_user_id_by_username(username=username)
        if not user_id:
            raise UserNotFoundException(f"User {username} not found")
        
        transaction = self.transaction_repo.exists(transaction_id=transaction_id)
        if not transaction:
            raise TransactionNotFoundException(f"Transaction with id {transaction_id} not found")
        
        return self.transaction_repo.fetch_one(
            transaction_id=transaction_id,
        )