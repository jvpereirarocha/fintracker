from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.base import get_db
from app.infra.repositories.categories import AdapterCategoryRepo
from app.usecases.categories.list_categories import ListCategoriesUseCase


async def get_list_categories_use_case(
    db: Session = Depends(get_db)
) -> ListCategoriesUseCase:
    category_repo = AdapterCategoryRepo(session=db)
    return ListCategoriesUseCase(category_repo=category_repo)

