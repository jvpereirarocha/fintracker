from app.domain.abstractions.repositories import AbstractCategoryRepository
from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.entities.base import PagedResponse
from app.domain.entities.categories import CategoryEntity


class ListCategoriesUseCase(AbstractUseCase):
    def __init__(self, category_repo: AbstractCategoryRepository) -> None:
        self.category_repo = category_repo

    async def execute(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> PagedResponse[CategoryEntity]:
        
        offset = (page - 1) * page_size
        
        categories, total = self.category_repo.fetch_all(
            page_size=page_size,
            offset=offset,
        )

        return PagedResponse(
            items=categories,
            total_count=total,
            page=page,
            items_per_page=page_size,
        )

