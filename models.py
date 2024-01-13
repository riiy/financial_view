import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
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
)

stocks = sa.Table(
    "stocks",
    metadata,
    sa.Column("symbol", sa.String, primary_key=True),
    sa.Column("name", sa.String, nullable=False, index=True),
    sa.Column("exchange", sa.String, nullable=False, index=True),
    sa.Column("price", sa.Float, nullable=True, comment="最新价"),
    sa.Column("change_percent", sa.Float, nullable=True, comment="涨跌幅"),
    sa.Column("change", sa.Float, nullable=True, comment="涨跌额"),
    sa.Column("volume", sa.Float, nullable=True, comment="成交量"),
    sa.Column("amount", sa.Float, nullable=True, comment="成交额"),
    sa.Column("amplitude", sa.Float, nullable=True, comment="振幅"),
    sa.Column("high", sa.Float, nullable=True, comment="最高"),
    sa.Column("low", sa.Float, nullable=True, comment="最低"),
    sa.Column("open", sa.Float, nullable=True, comment="今开"),
    sa.Column("previous_close", sa.Float, nullable=True, comment="昨收"),
    sa.Column("volume_rate", sa.Float, nullable=True, comment="量比"),
    sa.Column("turnover_rate", sa.Float, nullable=True, comment="换手率"),
    sa.Column("pe", sa.Float, nullable=True, comment="市盈率-动态"),
    sa.Column("pb", sa.Float, nullable=True, comment="市净率"),
    sa.Column("market_value", sa.Float, nullable=True, comment="总市值"),
    sa.Column("circulat_value", sa.Float, nullable=True, comment="流通市值"),
    sa.Column("growth_rate", sa.Float, nullable=True, comment="涨速"),
    sa.Column("minute_5_growth", sa.Float, nullable=True, comment="5分钟涨跌"),
    sa.Column("day_60_growth", sa.Float, nullable=True, comment="60日涨跌幅"),
    sa.Column("this_year_growth", sa.Float, nullable=True, comment="年初至今涨跌幅"),
    sa.Column("key", sa.String, server_default=sa.text("gen_random_uuid()")),
    schema="public",
)

gold_list = sa.Table(
    "gold_list",
    metadata,
    sa.Column("symbol", sa.String, primary_key=True),
    sa.Column("title", sa.String, nullable=False),
    sa.Column("tags", postgresql.ARRAY(sa.String)),
    sa.Column("description", sa.Text, nullable=True),
    sa.Column(
        "create_time",
        sa.DateTime(timezone=True),
        nullable=False,
        index=True,
        server_default=func.now(),
    ),
    sa.Column("key", sa.String, server_default=sa.text("gen_random_uuid()")),
    schema="public",
)
