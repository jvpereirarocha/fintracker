from fastapi import FastAPI
from app.routes.users import users_router
from app.routes.transactions import transactions_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Fintracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(router=users_router)
app.include_router(router=transactions_router)
