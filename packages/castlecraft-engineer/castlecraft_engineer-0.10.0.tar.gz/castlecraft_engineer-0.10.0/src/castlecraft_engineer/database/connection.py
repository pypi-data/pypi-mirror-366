from os import environ
from typing import Any, Dict, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from castlecraft_engineer.common.env import (
    ENV_ENABLE_SQL_LOG,
    ENV_SQL_ASYNC_CONNECTION_STRING,
    ENV_SQL_CONNECTION_STRING,
)


def get_engine(db_config: Optional[Dict[str, Any]] = None) -> Engine:
    """
    Creates and returns a new synchronous SQLAlchemy Engine.

    Configuration is sourced from the `db_config` dictionary, falling back
    to environment variables, and then to defaults.

    Args:
        db_config: A dictionary with optional 'connection_string',
                   'enable_sql_log', and other keyword arguments for
                   SQLAlchemy's `create_engine`.

    Returns:
        A new SQLAlchemy Engine instance.
    """
    config = db_config or {}
    engine_kwargs = config.copy()

    connection_string = engine_kwargs.pop(
        "connection_string",
        environ.get(ENV_SQL_CONNECTION_STRING, "sqlite:///db.sqlite3"),
    )
    if not connection_string:
        raise ValueError(
            f"Database connection string not found in config or {ENV_SQL_CONNECTION_STRING}."
        )

    enable_sql_log_str = str(
        engine_kwargs.pop("enable_sql_log", environ.get(ENV_ENABLE_SQL_LOG, "false"))
    ).lower()
    enable_sql_log = enable_sql_log_str in ("true", "1", "yes", "on")

    if "echo" not in engine_kwargs:
        engine_kwargs["echo"] = enable_sql_log

    return create_engine(connection_string, **engine_kwargs)


def get_async_engine(db_config: Optional[Dict[str, Any]] = None) -> AsyncEngine:
    """
    Creates and returns a new asynchronous SQLAlchemy AsyncEngine.

    Configuration is sourced from the `db_config` dictionary, falling back
    to environment variables, and then to defaults.

    Args:
        db_config: A dictionary with optional 'async_connection_string',
                   'enable_sql_log', and other keyword arguments for
                   SQLAlchemy's `create_async_engine`.

    Returns:
        A new SQLAlchemy AsyncEngine instance.
    """
    config = db_config or {}
    engine_kwargs = config.copy()

    async_db_url = engine_kwargs.pop(
        "async_connection_string",
        environ.get(ENV_SQL_ASYNC_CONNECTION_STRING, "sqlite+aiosqlite:///db.sqlite3"),
    )
    if not async_db_url:
        raise ValueError(
            f"Async database connection string not found in config or {ENV_SQL_ASYNC_CONNECTION_STRING}."
        )

    enable_sql_log_str = str(
        engine_kwargs.pop("enable_sql_log", environ.get(ENV_ENABLE_SQL_LOG, "false"))
    ).lower()
    enable_sql_log = enable_sql_log_str in ("true", "1", "yes", "on")

    if "echo" not in engine_kwargs:
        engine_kwargs["echo"] = enable_sql_log

    return create_async_engine(async_db_url, **engine_kwargs)
