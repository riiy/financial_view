"""first init

Revision ID: e45b77fcdcf8
Revises: 
Create Date: 2023-12-20 15:56:03.392045

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e45b77fcdcf8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

create_func = """CREATE or replace FUNCTION update_update_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.update_time = now();
    RETURN NEW;
END;
$$ language 'plpgsql';"""

drop_func = "drop function update_update_time;"

def upgrade() -> None:
    op.execute(create_func)


def downgrade() -> None:
    op.execute(drop_func)
