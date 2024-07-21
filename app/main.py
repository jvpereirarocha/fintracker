from typing import Annotated
from fastapi import Depends, FastAPI

from app.dependencies import get_db

app = FastAPI(title="Fintracker API")

@app.get("/")
def read_root(db: Annotated[None, Depends(get_db)]):
    print(f"DB: {dir(db)}")
    return {"message": "hello, world!"}
