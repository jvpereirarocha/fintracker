"""add user_id to expense unique index

Revision ID: 9b1e7c2d4a10
Revises: f4ed6ec7d419
Create Date: 2026-10-26 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9b1e7c2d4a10"
down_revision: str | None = "f4ed6ec7d419"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(
        "description_expense_due_date_idx",
        table_name="transactions",
        postgresql_where=sa.text("type_of_transaction = 'expense'"),
    )
    op.create_index(
        "description_expense_due_date_idx",
        "transactions",
        ["user_id", "description", "type_of_transaction", "due_date"],
        unique=True,
        postgresql_where=sa.text("type_of_transaction = 'expense'"),
    )


def downgrade() -> None:
    op.drop_index(
        "description_expense_due_date_idx",
        table_name="transactions",
        postgresql_where=sa.text("type_of_transaction = 'expense'"),
    )
    op.create_index(
        "description_expense_due_date_idx",
        "transactions",
        ["description", "type_of_transaction", "due_date"],
        unique=True,
        postgresql_where=sa.text("type_of_transaction = 'expense'"),
    )
