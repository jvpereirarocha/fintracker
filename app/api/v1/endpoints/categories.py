
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies.categories import get_list_categories_use_case
from app.api.v1.dtos.categories import PaginatedCategories
from app.dependencies import get_current_user
from app.usecases.categories.list_categories import ListCategoriesUseCase


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
    request: Request,
    items_per_page: Annotated[int, Query(alias="itemsPerPage")] = 10,
    page: Annotated[int, Query(alias="page")] = 1,
    use_case: ListCategoriesUseCase = Depends(get_list_categories_use_case)
):
    current_user = request.state.user

    return await use_case.execute(
        page=page,
        page_size=items_per_page,
    )
