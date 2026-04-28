from app.domain.abstractions.repositories import (
    AbstractCategoryRepository,
)
from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.exceptions.categories import CategoryNotFoundException


class DeleteCategoryUseCase(AbstractUseCase):
    def __init__(self, category_repo: AbstractCategoryRepository):
        self.category_repo = category_repo

    async def execute(
        self,
        category_id: int,
    ) -> None:
        category = self.category_repo.get_category_by_id(category_id=category_id)
        if not category:
            raise CategoryNotFoundException(f"Category with id {category_id} not found")

        return self.category_repo.delete(
            category_id=category_id,
        )
