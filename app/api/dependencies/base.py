from fastapi import Depends, Query, Request

from app.database import Session
from app.domain.value_objects.auth import JWTPayload
from app.domain.value_objects.pagination import PaginationParams
from app.infra.auth.token import TokenProvider


def get_current_user(
    request: Request,
    token_provider: TokenProvider = Depends(TokenProvider),
) -> JWTPayload:
    token_data = token_provider.decode_token(request=request)
    request.state.user = token_data
    return token_data

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
