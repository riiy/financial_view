import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()
metadata = Base.metadata

create_func = """CREATE FUNCTION update_update_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.update_time = now();
    RETURN NEW;
END;
$$ language 'plpgsql';"""
user = sa.Table(
    "user",
    metadata,
    sa.Column("email", sa.String, primary_key=True),
    sa.Column("create_time", sa.DateTime(timezone=True), nullable=False, index=True, server_default=func.now()),
    sa.Column("update_time", sa.DateTime(timezone=True), nullable=False, index=True, server_default=func.now()),
    schema='auth'
)

# stock = sa.Table(
#     "stock",
#     metadata,
#     sa.Column("sysmbol", sa.String, primary_key=True),
#     sa.Column("name", sa.String, nullable=False, index=True),
#     sa.Column("price", sa.FLOAT),
#     sa.Column("change", sa.FLOAT),
# )
