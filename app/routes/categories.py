from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.database import Category, User
from app.dependencies import get_current_user, get_session
from app.schemas.categories import AllCategoriesResponse, CategorySchemaResponse, NewCategoryResponse, NewCategorySchema, UpdateCategorySchema


category_router = APIRouter(
    prefix="category/",
    dependencies=[Depends(get_session), Depends(get_current_user)]
)

@category_router.post(
    "/",
    response_model=NewCategoryResponse,
    status_code=HTTPStatus.CREATED,
)
async def create_new_category(request: Request, category_dto: NewCategorySchema):
    current_user = request.state.user
    session = await get_session()
    db_user = session.scalar(select(User).where((User.username == current_user.sub)))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")
    
    category = session.scalar(
        select(Category)
        .where(Category.name == category_dto.name.lower())
    )
    if category:
        raise HTTPException(detail="The category already exists and cannot be persisted again!", status_code=HTTPStatus.BAD_REQUEST)
    
    new_category = Category(name=category_dto.name, description=category_dto.description)
    session.add(new_category)
    session.commit()
    
    return NewCategoryResponse()


@category_router.get(
    "/{category_id}",
    response_model=CategorySchemaResponse,
    status_code=HTTPStatus.OK,
)
async def get_category(request: Request, category_id: int, update_category_dto: UpdateCategorySchema):
    current_user = request.state.user
    session = await get_session()
    db_user = session.scalar(select(User).where((User.username == current_user.sub)))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")
    
    category = session.scalar(
        select(Category)
        .where(Category.category_id == category_id)
    )
    if not category:
        raise HTTPException(detail="The category doesn't exist", status_code=HTTPStatus.NOT_FOUND)
    
    return CategorySchemaResponse.model_validate(obj=category)


@category_router.get(
    "/",
    response_model=AllCategoriesResponse,
    status_code=HTTPStatus.OK,
)
async def get_all_categories(request: Request):
    current_user = request.state.user
    session = await get_session()
    db_user = session.scalar(select(User).where((User.username == current_user.sub)))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")
    
    categories = session.scalars(
        select(Category)
    )
    if not categories:
        raise HTTPException(detail="The category doesn't exist", status_code=HTTPStatus.NOT_FOUND)
    
    return AllCategoriesResponse(
        results=[CategorySchemaResponse.model_validate(obj=category) for category in categories]
    )


@category_router.patch(
    "/{category_id}",
    response_model=CategorySchemaResponse,
    status_code=HTTPStatus.OK,
)
async def update_category(request: Request, category_id: int, update_category_dto: UpdateCategorySchema):
    current_user = request.state.user
    session = await get_session()
    db_user = session.scalar(select(User).where((User.username == current_user.sub)))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")
    
    category = session.scalar(
        select(Category)
        .where(Category.category_id == category_id)
    )
    if not category:
        raise HTTPException(detail="The category doesn't exist", status_code=HTTPStatus.BAD_REQUEST)

    
    updated_values_of_category = update_category_dto.model_dump(exclude_none=True, exclude_unset=True)

    for key, value in updated_values_of_category.items():
        if value is not None:
            setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh()
    return CategorySchemaResponse.model_validate(obj=category)


@category_router.delete(
    "/{category_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_category(request: Request, category_id: int):
    current_user = request.state.user
    session = await get_session()
    db_user = session.scalar(select(User).where((User.username == current_user.sub)))
    if not db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")
    
    category = session.scalar(
        select(Category)
        .where(Category.category_id == category_id)
    )
    if not category:
        raise HTTPException(detail="The category doesn't exist", status_code=HTTPStatus.BAD_REQUEST)

    session.delete(category)
    session.commit()
    return JSONResponse(content=None)