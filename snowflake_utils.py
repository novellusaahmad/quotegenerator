from datetime import date, datetime
from decimal import Decimal

from flask import current_app

try:
    import snowflake.connector as snowflake_connector
except Exception:  # pragma: no cover - dependency may be missing in some environments
    snowflake_connector = None


def set_snowflake_config(config: dict) -> None:
    """Store Snowflake connection configuration in the Flask app config."""
    current_app.config["SNOWFLAKE_CONFIG"] = config


def _get_snowflake_connection():
    cfg = current_app.config.get("SNOWFLAKE_CONFIG")
    if not cfg:
        return None
    if snowflake_connector is None:
        raise RuntimeError("snowflake-connector-python is not installed")
    return snowflake_connector.connect(
        user=cfg.get("user"),
        password=cfg.get("password"),
        account=cfg.get("account"),
        warehouse=cfg.get("warehouse"),
        database=cfg.get("database"),
        schema=cfg.get("schema"),
    )


def test_snowflake_connection() -> None:
    """Attempt to connect to Snowflake using current configuration.

    Raises
    ------
    RuntimeError
        If the connection configuration is missing or the connection fails.
    """
    conn = _get_snowflake_connection()
    if conn is None:
        raise RuntimeError("Snowflake connection is not configured")
    conn.close()


def sync_data_to_snowflake(table: str, rows):
    """Insert rows into the given Snowflake table.

    Parameters
    ----------
    table: str
        Destination table name.
    rows: dict or list[dict]
        Data to insert. Each dict represents a row.
    """
    conn = _get_snowflake_connection()
    if conn is None:
        raise RuntimeError("Snowflake connection is not configured")

    if isinstance(rows, dict):
        rows = [rows]
    if not rows:
        return

    columns = list(rows[0].keys())
    create_stmt = "create table if not exists {0} ({1})".format(
        table,
        ", ".join(f"{c} variant" for c in columns),
    )
    insert_stmt = "insert into {0} ({1}) values ({2})".format(
        table,
        ", ".join(columns),
        ", ".join(["%s"] * len(columns)),
    )

    cs = conn.cursor()
    try:
        cs.execute(create_stmt)
        for row in rows:
            cs.execute(insert_stmt, [row.get(col) for col in columns])
        conn.commit()
    finally:
        cs.close()
        conn.close()


def model_to_dict(model) -> dict:
    """Convert a SQLAlchemy model to a plain dict suitable for Snowflake."""
    result = {}
    for column in model.__table__.columns:  # type: ignore[attr-defined]
        value = getattr(model, column.name)
        if isinstance(value, Decimal):
            value = float(value)
        elif isinstance(value, (date, datetime)):
            value = value.isoformat()
        result[column.name] = value
    return result

