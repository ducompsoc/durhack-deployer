"""create event table

Revision ID: ac20ac7bcea6
Revises: 
Create Date: 2024-10-08 18:13:07.166089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac20ac7bcea6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'event',
        sa.Column('id', sa.String, primary_key=True),
    )


def downgrade() -> None:
    op.drop_table('event')
