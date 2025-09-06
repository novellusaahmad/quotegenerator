"""Utility helpers for optional Snowflake integration."""

from datetime import date, datetime
from decimal import Decimal
import json
import os

from flask import current_app

try:
    import snowflake.connector as snowflake_connector
except Exception:  # pragma: no cover - dependency may be missing in some environments
    snowflake_connector = None


# Path where Snowflake configuration is persisted for reuse across requests
SNOWFLAKE_CONFIG_FILE = "snowflake_config.json"


def set_snowflake_config(config: dict) -> None:
    """Store Snowflake connection configuration and persist to disk.

    Parameters
    ----------
    config: dict
        Configuration values received from the frontend.
    """

    current_app.config["SNOWFLAKE_CONFIG"] = config

    # Persist configuration so it survives application restarts or
    # cross-process requests. Failures here shouldn't break the request.
    try:  # pragma: no cover - IO failures are non-critical
        with open(SNOWFLAKE_CONFIG_FILE, "w") as f:
            json.dump(config, f)
    except Exception as exc:
        current_app.logger.warning(f"Failed to persist Snowflake config: {exc}")


def get_snowflake_config() -> dict:
    """Return the current Snowflake configuration.

    The configuration is first looked up in ``current_app.config`` and, if not
    present, loaded from the persisted JSON file. This allows the application
    to reuse saved settings even after a restart.
    """

    cfg = current_app.config.get("SNOWFLAKE_CONFIG")
    if cfg:
        return cfg

    if os.path.exists(SNOWFLAKE_CONFIG_FILE):
        try:  # pragma: no cover - IO failures are non-critical
            with open(SNOWFLAKE_CONFIG_FILE, "r") as f:
                cfg = json.load(f)
            current_app.config["SNOWFLAKE_CONFIG"] = cfg
            return cfg
        except Exception as exc:
            current_app.logger.warning(f"Failed to load Snowflake config: {exc}")

    return {}


def _get_snowflake_connection():
    cfg = get_snowflake_config()
    if not cfg:
        return None
    if snowflake_connector is None:
        raise RuntimeError("snowflake-connector-python is not installed")
    method = cfg.get("method")
    if method == "token":
        return snowflake_connector.connect(
            account=cfg.get("account"),
            warehouse=cfg.get("warehouse"),
            database=cfg.get("database"),
            schema=cfg.get("schema"),
            token=cfg.get("token"),
            authenticator="oauth",
        )
    password = cfg.get("password")
    if method == "pat":
        password = cfg.get("token")
    return snowflake_connector.connect(
        user=cfg.get("user"),
        password=password,
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


def ensure_snowflake_table(conn, table: str, sample) -> None:
    """Ensure ``table`` exists in Snowflake and has required columns.

    Parameters
    ----------
    conn:
        Active Snowflake connection.
    table: str
        Destination table name.
    sample: dict or SQLAlchemy model
        Object used to derive the table schema.

    Notes
    -----
    Columns are created using the ``VARIANT`` type which accepts arbitrary
    JSON-compatible values. Any schema changes are logged for auditing.
    """

    if not sample:
        return

    if hasattr(sample, "__table__"):
        columns = [c.name for c in sample.__table__.columns]  # type: ignore[attr-defined]
    else:
        columns = list(sample.keys())

    cs = conn.cursor()
    try:
        cs.execute(f"show tables like '{table}'")
        exists = cs.fetchone() is not None
        if not exists:
            create_stmt = f"create table {table} ({', '.join(f'{c} variant' for c in columns)})"
            cs.execute(create_stmt)
            conn.commit()
            current_app.logger.info("Created Snowflake table %s with columns %s", table, ", ".join(columns))
            return

        cs.execute(f"describe table {table}")
        existing_cols = {row[0].upper() for row in cs.fetchall()}
        missing = [c for c in columns if c.upper() not in existing_cols]
        for col in missing:
            cs.execute(f"alter table {table} add column {col} variant")
            current_app.logger.info("Added column %s to Snowflake table %s", col, table)
        if missing:
            conn.commit()
    finally:
        cs.close()


def sync_data_to_snowflake(table: str, rows):
    """Insert rows into a Snowflake table, creating/altering the table if needed.

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

    ensure_snowflake_table(conn, table, rows[0])

    def _prepare_value(val):
        """JSON-encode ``val`` for safe ``VARIANT`` insertion.

        Snowflake expects ``VARIANT`` values to be provided as JSON strings and
        converted using ``parse_json``. Serialising *all* values (including
        numbers and strings) keeps the behaviour uniform and allows
        ``parse_json`` to correctly recreate the original types. Any value that
        cannot be serialised is converted to its string representation.
        """

        try:
            return json.dumps(val)
        except Exception:
            return json.dumps(str(val))

    columns = list(rows[0].keys())
    placeholders = ["parse_json(%s)" for _ in columns]
    insert_stmt = "insert into {0} ({1}) values ({2})".format(
        table,
        ", ".join(columns),
        ", ".join(placeholders),
    )

    cs = conn.cursor()
    try:
        for row in rows:
            params = [_prepare_value(row.get(col)) for col in columns]
            cs.execute(insert_stmt, params)
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

