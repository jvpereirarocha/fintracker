from fastapi import FastAPI
from app.routes.users import users_router
# from app.routes.transactions import transactions_router
# from app.routes.dashboard import dashboard_router
from app.routes.categories import category_router
from app.api.v1 import api_v1_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Fintracker API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router=api_v1_router)
app.include_router(router=users_router)
# app.include_router(router=transactions_router)
# app.include_router(router=dashboard_router)
app.include_router(router=category_router)
