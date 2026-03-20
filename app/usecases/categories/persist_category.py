from app.domain.abstractions.usecases import AbstractUseCase
from app.domain.abstractions.repositories import (
    AbstractCategoryRepository,
)
from app.domain.entities.categories import SaveCategory, PartialUpdateCategory, CategoryEntity
from app.domain.exceptions.categories import CategoryAlreadyExistsException, CategoryNotFoundException


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
            raise CategoryAlreadyExistsException(f"Category {new_category.name} already exists")
        
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
        
        category = self.category_repo.get_category_by_id(category_id=category_id)
        if not category:
            raise CategoryNotFoundException(
                message=f"Category with id {category_id} not found"
            )
        
        category_with_the_same_name_already_exists = False
        if edit_category.name:
            found_category_id =  self.category_repo.get_category_id_by_name(name=edit_category.name)
            category_with_the_same_name_already_exists = bool(
                found_category_id and found_category_id != category_id
            )
        
        if category_with_the_same_name_already_exists:
            raise CategoryAlreadyExistsException(
                message=f"Category {edit_category.name} already exists"
            )
        
        return self.category_repo.update(
            category_id=category_id,
            edit_category=edit_category,
        )
        