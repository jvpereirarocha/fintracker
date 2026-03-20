from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.abstractions.repositories import (
    AbstractCategoryRepository,
)


class DeleteCategoryUseCase(AbstractUseCase):
    def __init__(
        self,
        category_repo: AbstractCategoryRepository
    ):
        self.category_repo = category_repo


    async def execute(
        self,
        category_id: int,
    ) -> None:
        
        return self.category_repo.delete(
            category_id=category_id,
        )
        