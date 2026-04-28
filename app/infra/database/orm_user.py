from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy.sql.sqltypes import LargeBinary

from app.infra.database.base import mapped_registry as base_mapped_registry


@base_mapped_registry.mapped_as_dataclass
class User:
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[bytes] = mapped_column(LargeBinary(60))
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())
