import sqlalchemy as sa
from sqlalchemy.sql import func

metadata = sa.MetaData()

user = sa.Table(
    "user",
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

stock = sa.Table(
    "stock",
    metadata,
    sa.Column("symbol", sa.String, primary_key=True),
    sa.Column("name", sa.String, nullable=False, index=True),
    schema="public",
)

profile = sa.Table(
    "profile",
    metadata,
    sa.Column("email", sa.String, sa.ForeignKey("auth.user.email"), primary_key=True),
    sa.Column("name", sa.String, nullable=True),
    schema="public",
)
