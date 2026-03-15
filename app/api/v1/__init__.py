from fastapi import APIRouter
from app.api.v1.endpoints.transactions import transactions_router

api_v1_router = APIRouter(
    prefix="/api/v1",
)

api_v1_router.include_router(router=transactions_router)