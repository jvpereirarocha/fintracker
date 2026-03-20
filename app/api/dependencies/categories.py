from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.base import get_db
from app.infra.repositories.categories import AdapterCategoryRepo
from app.usecases.categories.list_categories import ListCategoriesUseCase, GetOneCategoryUseCase
from app.usecases.categories.persist_category import CreateCategoryUseCase, UpdateCategoryUseCase
from app.usecases.categories.delete_category import DeleteCategoryUseCase


async def get_list_categories_use_case(
    db: Session = Depends(get_db)
) -> ListCategoriesUseCase:
    category_repo = AdapterCategoryRepo(session=db)
    return ListCategoriesUseCase(category_repo=category_repo)


async def get_one_category_use_case(
    db: Session = Depends(get_db)
) -> GetOneCategoryUseCase:
    category_repo = AdapterCategoryRepo(session=db)
    return GetOneCategoryUseCase(category_repo=category_repo)


async def get_create_category_use_case(
    db: Session = Depends(get_db)
) -> CreateCategoryUseCase:
    category_repo = AdapterCategoryRepo(session=db)
    return CreateCategoryUseCase(category_repo=category_repo)


async def get_update_category_use_case(
    db: Session = Depends(get_db)
) -> UpdateCategoryUseCase:
    category_repo = AdapterCategoryRepo(session=db)
    return UpdateCategoryUseCase(category_repo=category_repo)


async def get_delete_category_use_case(
    db: Session = Depends(get_db)
) -> DeleteCategoryUseCase:
    category_repo = AdapterCategoryRepo(session=db)
    return DeleteCategoryUseCase(category_repo=category_repo)