from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.abstractions.repositories import (
    AbstractCategoryRepository,
)
from app.domain.entities.categories import SaveCategory, PartialUpdateCategory, CategoryEntity


class CreateCategoryUseCase(AbstractUseCase):
    def __init__(
        self,
        category_repo: AbstractCategoryRepository
    ):
        self.category_repo = category_repo


    async def execute(
        self,
        new_category: SaveCategory,
    ) -> CategoryEntity:
        
        category_id = self.category_repo.get_category_id_by_name(name=new_category.name)
        if category_id:
            raise ValueError(f"Category {new_category.name} already exists")
        
        return self.category_repo.save(
            new_category=new_category,
        )
        

class UpdateCategoryUseCase(AbstractUseCase):
    def __init__(
        self,
        category_repo: AbstractCategoryRepository
    ):
        self.category_repo = category_repo


    async def execute(
        self,
        category_id: int,
        edit_category: PartialUpdateCategory,
    ) -> CategoryEntity:
        
        category_already_exists = False
        if edit_category.name:
            found_category_id =  self.category_repo.get_category_id_by_name(name=edit_category.name)
            category_already_exists = found_category_id and found_category_id != category_id
        
        if category_already_exists:
            raise ValueError(f"Category {edit_category.name} already exists")
        
        return self.category_repo.update(
            category_id=category_id,
            edit_category=edit_category,
        )
        