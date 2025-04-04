"""added due date unique index

Revision ID: 3c76e05b0b4e
Revises: 0aea5ffcd66b
Create Date: 2024-11-04 19:23:16.383746

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "3c76e05b0b4e"
down_revision: Union[str, None] = "0aea5ffcd66b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("transactions", sa.Column("due_date", sa.Date(), nullable=True))
    op.alter_column(
        "transactions",
        "registration_date",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.Date(),
        existing_nullable=True,
    )
    op.create_index(
        "description_expense_due_date_idx",
        "transactions",
        ["description", "type_of_transaction", "due_date"],
        unique=True,
        postgresql_where=sa.text("type_of_transaction = 'expense'"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "description_expense_due_date_idx",
        table_name="transactions",
        postgresql_where=sa.text("type_of_transaction = 'expense'"),
    )
    op.alter_column(
        "transactions",
        "registration_date",
        existing_type=sa.Date(),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
    )
    op.drop_column("transactions", "due_date")
    # ### end Alembic commands ###
