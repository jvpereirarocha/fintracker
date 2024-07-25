from app.database import Session


async def get_session():
    with Session() as session:
        return session