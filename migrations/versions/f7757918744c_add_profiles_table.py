"""add profiles table

Revision ID: f7757918744c
Revises: 99bf025c0ebb
Create Date: 2024-01-02 17:33:26.325216

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7757918744c'
down_revision: Union[str, None] = '99bf025c0ebb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('profiles',
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['email'], ['auth.users.email'], ),
    sa.PrimaryKeyConstraint('email'),
    schema='public'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('profiles', schema='public')
    # ### end Alembic commands ###
