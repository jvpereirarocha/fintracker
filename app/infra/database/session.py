import sqlalchemy
from sqlalchemy.orm import sessionmaker

from app.infra.configs.settings import Settings

# hide_parameters: SQLAlchemy errors otherwise embed the bound values ("[parameters: (...)]")
# in their message, and the 500 handler logs that message to logs that leave the cluster
engine = sqlalchemy.create_engine(url=Settings().DATABASE_URL, hide_parameters=True)  # type: ignore

LocalSessionMaker = sessionmaker(engine)
