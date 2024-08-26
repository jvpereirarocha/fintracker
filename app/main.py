from fastapi import FastAPI
from app.routes.users import users_router


app = FastAPI(title="Fintracker API")


app.include_router(router=users_router)
