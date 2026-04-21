from datetime import datetime

from sqlalchemy import Index, String, func, text
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.infra.database.base import mapped_registry as base_mapped_registry


@base_mapped_registry.mapped_as_dataclass
class Category:
    __tablename__ = "category"

    category_id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())

    __table_args__ = (
        Index("category_lower_name_idx", func.lower(text("name"))),
    )
