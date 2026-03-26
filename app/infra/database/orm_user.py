from datetime import datetime

from sqlalchemy import Index, func
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy.sql.sqltypes import LargeBinary

from app.infra.database.base import mapped_registry as base_mapped_registry


@base_mapped_registry.mapped_as_dataclass
class User:
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[bytes] = mapped_column(LargeBinary(60))
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())

    __table_args__ = (
        Index("user_email_pass_idx", "username", "email", "password_hash"),
        Index("email_pass_idx", "email", "password_hash"),
        Index("user_pass_idx", "username", "password_hash"),
        Index("user_created_at_idx", "username", "created_at"),
        Index("email_created_at_idx", "email", "created_at"),
        Index("user_updated_at_idx", "username", "updated_at"),
        Index("email_updated_at_idx", "email", "updated_at"),
    )
