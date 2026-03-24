"""remove password_salt column

Revision ID: 480e3d108c2a
Revises: b05a5659e069
Create Date: 2026-03-23 20:55:05.018698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '480e3d108c2a'
down_revision: Union[str, None] = 'b05a5659e069'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(index_name='user_email_pass_idx', table_name='users', if_exists=True)
    op.drop_index(index_name='email_pass_idx', table_name='users', if_exists=True)
    op.drop_index(index_name='user_pass_idx', table_name='users', if_exists=True)
    op.drop_column(table_name='users', column_name='password_salt')
    op.create_index(
        index_name='user_email_pass_idx',
        table_name='users',
        columns=[
            'username',
            'email',
            'password_hash'
        ],
        if_not_exists=True
    )
    op.create_index(
        index_name='user_pass_idx',
        table_name='users',
        columns=[
            'username',
            'password_hash'
        ],
        if_not_exists=True
    )
    op.create_index(
        index_name='email_pass_idx',
        table_name='users',
        columns=[
            'email',
            'password_hash'
        ],
        if_not_exists=True
    )


def downgrade() -> None:
    op.add_column(
        table_name='users',
        column=sa.Column(
            'password_salt',
            sa.LargeBinary(length=29), nullable=False
        )
    )
    op.drop_index(index_name='user_email_pass_idx', table_name='users', if_exists=True)
    op.drop_index(index_name='email_pass_idx', table_name='users', if_exists=True)
    op.drop_index(index_name='user_pass_idx', table_name='users', if_exists=True)
    op.create_index(
        index_name='user_email_pass_idx',
        table_name='users',
        columns=[
            'username',
            'email',
            'password_hash',
            'password_salt',
        ],
        if_not_exists=True
    )
    op.create_index(
        index_name='email_pass_idx',
        table_name='users',
        columns=[
            'email',
            'password_hash',
            'password_salt',
        ],
        if_not_exists=True
    )
    op.create_index(
        index_name='user_pass_idx',
        table_name='users',
        columns=[
            'username',
            'password_hash',
            'password_salt',
        ],
        if_not_exists=True
    )
