
from http import HTTPStatus

from fastapi import APIRouter, Depends

from app.api.dependencies.base import get_pagination_params
from app.api.dependencies.categories import (
    get_list_categories_use_case,
    get_one_category_use_case,
    get_create_category_use_case,
    get_update_category_use_case,
    get_delete_category_use_case
)
from app.api.v1.dtos.categories import CategoryResponse, PaginatedCategories, SaveCategoryDTO, UpdatePartialCategoryDTO
from app.dependencies import get_current_user
from app.domain.entities.categories import PartialUpdateCategory, SaveCategory
from app.domain.value_objects.pagination import PaginationParams
from app.usecases.categories.list_categories import ListCategoriesUseCase, GetOneCategoryUseCase
from app.usecases.categories.persist_category import CreateCategoryUseCase, UpdateCategoryUseCase
from app.usecases.categories.delete_category import DeleteCategoryUseCase


categories_router = APIRouter(
    prefix="/categories",
    dependencies=[Depends(get_current_user)],
)

@categories_router.get(
    path="/",
    response_model=PaginatedCategories,
    status_code=HTTPStatus.OK,
)
async def get_all_categories(
    pagination: PaginationParams =  Depends(get_pagination_params),
    use_case: ListCategoriesUseCase = Depends(get_list_categories_use_case)
):
    return await use_case.execute(pagination=pagination)


@categories_router.get(
    path="/{category_id}",
    response_model=CategoryResponse,
    status_code=HTTPStatus.OK,
)
async def fetch_one_category(
    category_id: int,
    use_case: GetOneCategoryUseCase = Depends(get_one_category_use_case)
):
    return await use_case.execute(
        category_id=category_id,
    )


@categories_router.post(
    path="/",
    response_model=CategoryResponse,
    status_code=HTTPStatus.CREATED,
)
async def create_new_category(
    payload: SaveCategoryDTO,
    use_case: CreateCategoryUseCase = Depends(get_create_category_use_case)
):
    new_category = SaveCategory(
        name=payload.name,
        description=payload.description,
    )
    
    return await use_case.execute(
        new_category=new_category
    )


@categories_router.patch(
    path="/{category_id}",
    response_model=CategoryResponse,
    status_code=HTTPStatus.OK,
)
async def edit_category(
    category_id: int,
    payload: UpdatePartialCategoryDTO,
    use_case: UpdateCategoryUseCase = Depends(get_update_category_use_case)
):
    edit_category = PartialUpdateCategory(
        name=payload.name,
        description=payload.description,
    )
    
    return await use_case.execute(
        category_id=category_id,
        edit_category=edit_category,
    )


@categories_router.delete(
    path="/{category_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_category(
    category_id: int,
    use_case: DeleteCategoryUseCase = Depends(get_delete_category_use_case)
):
    return await use_case.execute(
        category_id=category_id,
    )