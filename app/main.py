from fastapi import FastAPI
from app.api.handlers import domain_exception_handler, global_500_exception_handler
from app.domain.exceptions.base import BaseDomainException
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

app.add_exception_handler(BaseDomainException, domain_exception_handler) # type: ignore
app.add_exception_handler(Exception, global_500_exception_handler)
