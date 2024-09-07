from fastapi import FastAPI
from app.routes.users import users_router
from app.routes.transactions import transactions_router


app = FastAPI(title="Fintracker API")


app.include_router(router=users_router)
app.include_router(router=transactions_router)
