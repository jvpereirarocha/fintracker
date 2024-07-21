from app.database import Session


async def get_db():
    with Session() as session:
        yield session