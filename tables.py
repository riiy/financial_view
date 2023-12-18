import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()
metadata = Base.metadata


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("email", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("code", sqlalchemy.INT),
    sqlalchemy.Column(
        "create_time",
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    sqlalchemy.Column(
        "update_time",
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
)


stocks = sqlalchemy.Table(
    "stocks",
    metadata,
    sqlalchemy.Column("sysmbol", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("price", sqlalchemy.FLOAT),
    sqlalchemy.Column("change", sqlalchemy.FLOAT),
)
