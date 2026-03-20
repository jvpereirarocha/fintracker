from app.domain.abstractions.repositories import AbstractCategoryRepository
from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.entities.base import PagedResponse
from app.domain.entities.categories import CategoryEntity
from app.domain.value_objects.pagination import PaginationParams


class ListCategoriesUseCase(AbstractUseCase):
    def __init__(self, category_repo: AbstractCategoryRepository) -> None:
        self.category_repo = category_repo

    async def execute(
        self,
        pagination: PaginationParams,
    ) -> PagedResponse[CategoryEntity]:
        
        categories, total = self.category_repo.fetch_all(
            limit=pagination.page_size,
            offset=pagination.offset,
        )

        return PagedResponse(
            items=categories,
            total_count=total,
            page=pagination.page,
            items_per_page=pagination.page_size,
        )


class GetOneCategoryUseCase(AbstractUseCase):
    def __init__(self, category_repo: AbstractCategoryRepository) -> None:
        self.category_repo = category_repo

    async def execute(
        self,
        category_id: int,
    ) -> CategoryEntity:
        
        return self.category_repo.fetch_one(
            category_id=category_id,
        )