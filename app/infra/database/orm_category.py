from datetime import datetime

from sqlalchemy import Index, String, func
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
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())

    __table_args__ = (
        Index("category_id_name_idx", "category_id", "name"),
        Index("category_id_description_idx", "category_id", "description"),
        Index("category_id_created_at_idx", "category_id", "created_at"),
        Index("category_id_updated_at_idx", "category_id", "updated_at"),
        Index("name_description_idx", "name", "description"),
        Index("category_id_name_description_idx", "category_id", "name", "description"),
        Index(
            "category_id_name_description_created_at_idx",
            "category_id",
            "name",
            "description",
            "created_at",
        ),
        Index(
            "category_id_name_description_created_at_updated_at_idx",
            "category_id",
            "name",
            "description",
            "created_at",
            "updated_at",
        ),
    )
