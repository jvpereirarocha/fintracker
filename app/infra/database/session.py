import sqlalchemy
from sqlalchemy.orm import sessionmaker

from app.infra.configs.settings import Settings

engine = sqlalchemy.create_engine(url=Settings().DATABASE_URL)  # type: ignore

LocalSessionMaker = sessionmaker(engine)
