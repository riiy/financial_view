import sqlalchemy as sa
from sqlalchemy.sql import func

metadata = sa.MetaData()

users = sa.Table(
    "users",
    metadata,
    sa.Column("email", sa.String, primary_key=True),
    sa.Column("verify_code", sa.String, nullable=True),
    sa.Column(
        "create_time",
        sa.DateTime(timezone=True),
        nullable=False,
        index=True,
        server_default=func.now(),
    ),
    sa.Column(
        "update_time",
        sa.DateTime(timezone=True),
        nullable=False,
        index=True,
        server_default=func.now(),
    ),
    schema="auth",
)

profiles = sa.Table(
    "profiles",
    metadata,
    sa.Column("email", sa.String, sa.ForeignKey("auth.users.email"), primary_key=True),
    sa.Column("name", sa.String, nullable=True),
    schema="public",
)

stocks = sa.Table(
    "stocks",
    metadata,
    sa.Column("symbol", sa.String, primary_key=True),
    sa.Column("name", sa.String, nullable=False, index=True),
    sa.Column("exchange", sa.String, nullable=False, index=True),
    schema="public",
)
