from fastapi import Query, Request

from app.database import Session
from app.domain.value_objects.pagination import PaginationParams
from app.middleware import get_user_info


async def get_current_user(request: Request):
    user_info = await get_user_info(request=request)
    request.state.user = user_info
    return user_info

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


def get_pagination_params(
    page: int = Query(1, ge=1, alias="page", description="Page number"),
    page_size: int = Query(10, ge=1, le=20, alias="itemsPerPage", description="Page size")
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)
