from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.abstractions.repositories import AbstractTransactionRepository
from app.domain.value_objects.transactions import TransactionsFilter
from app.domain.entities.base import PagedResponse
from app.domain.entities.transactions import TransactionEntity


class ListTransactionsUseCase(AbstractUseCase):
    def __init__(self, repo: AbstractTransactionRepository):
        self.repo = repo

    def execute(
        self,
        filters: TransactionsFilter,
        page: int,
        page_size: int
    ) -> PagedResponse[TransactionEntity]:
        
        items, total = self.repo.fetch_all(
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