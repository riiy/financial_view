"""add stock

Revision ID: 3bbf5ac5a225
Revises: 99bf025c0ebb
Create Date: 2023-12-20 16:17:15.666647

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3bbf5ac5a225'
down_revision: Union[str, None] = '99bf025c0ebb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stock',
    sa.Column('sysmbol', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('price', sa.FLOAT(), nullable=True),
    sa.Column('change', sa.FLOAT(), nullable=True),
    sa.PrimaryKeyConstraint('sysmbol')
    )
    op.create_index(op.f('ix_stock_name'), 'stock', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_stock_name'), table_name='stock')
    op.drop_table('stock')
    # ### end Alembic commands ###