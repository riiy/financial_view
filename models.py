import sqlalchemy as sa
from sqlalchemy.sql import func

metadata = sa.MetaData()

user = sa.Table(
    "user",
    metadata,
    sa.Column("email", sa.String, primary_key=True),
    sa.Column("create_time", sa.DateTime(timezone=True), nullable=False, index=True, server_default=func.now()),
    sa.Column("update_time", sa.DateTime(timezone=True), nullable=False, index=True, server_default=func.now()),
    schema='auth'
)

stock = sa.Table(
    "stock",
    metadata,
    sa.Column("sysmbol", sa.String, primary_key=True),
    sa.Column("name", sa.String, nullable=False, index=True),
    sa.Column("price", sa.FLOAT),
    sa.Column("change", sa.FLOAT),
)
