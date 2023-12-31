"""add uuid

Revision ID: 9a1b9a8cd56d
Revises: 7cda2a48d41f
Create Date: 2024-01-04 14:25:22.196631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a1b9a8cd56d'
down_revision: Union[str, None] = '7cda2a48d41f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gold_list', sa.Column('key', sa.String(), server_default=sa.text('gen_random_uuid()'), nullable=True))
    op.add_column('stocks', sa.Column('key', sa.String(), server_default=sa.text('gen_random_uuid()'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stocks', 'key')
    op.drop_column('gold_list', 'key')
    # ### end Alembic commands ###
