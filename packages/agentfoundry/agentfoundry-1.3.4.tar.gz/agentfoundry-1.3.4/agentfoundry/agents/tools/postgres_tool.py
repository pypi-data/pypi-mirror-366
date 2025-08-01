"""PostgreSQL query execution tool.

The tool expects a SQL *query* string and optional *connection_uri*.
If *connection_uri* is omitted, it uses the `POSTGRES_URI` value from the
Agentfoundry configuration or the environment variable of the same name.

Only **SELECT** statements are allowed – mutating queries are rejected for
safety reasons.
"""

from __future__ import annotations

import os
import re
from typing import Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field, validator

from agentfoundry.utils.config import Config
from agentfoundry.utils.logger import get_logger


logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Input schema
# ---------------------------------------------------------------------------


class _PGInput(BaseModel):
    query: str = Field(..., description="SQL SELECT query to run against PostgreSQL")
    connection_uri: Optional[str] = Field(
        None,
        description="PostgreSQL connection string. If omitted, POSTGRES_URI config/env is used.",
    )

    @validator("query")
    def select_only(cls, v: str):  # noqa: D401
        if not re.match(r"^\s*SELECT", v, re.IGNORECASE):
            raise ValueError("Only SELECT statements are allowed")
        return v


# ---------------------------------------------------------------------------
# Core implementation
# ---------------------------------------------------------------------------


def _run_pg_query(query: str, connection_uri: Optional[str] = None):  # noqa: D401
    conn_uri = connection_uri or Config().get("POSTGRES.URI") or os.getenv("POSTGRES_URI")
    if not conn_uri:
        return "PostgreSQL connection URI not provided (via arg or POSTGRES_URI)."

    try:
        import pg8000.dbapi as pg  # type: ignore
    except ModuleNotFoundError:
        return "pg8000 package not installed; install with 'pip install pg8000'."

    # pg8000 does not accept a full URI directly; parse components
    from urllib.parse import urlparse, unquote

    try:
        parsed = urlparse(conn_uri)
        if not parsed.scheme.startswith("postgres"):
            return "Invalid postgres URI scheme."

        conn_kwargs = {
            "user": unquote(parsed.username) if parsed.username else None,
            "password": unquote(parsed.password) if parsed.password else None,
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 5432,
            "database": parsed.path.lstrip("/") or None,
        }

        # Remove None values so pg8000 can fall back to defaults
        conn_kwargs = {k: v for k, v in conn_kwargs.items() if v is not None}

        conn = pg.connect(**conn_kwargs)
    except Exception as exc:  # pragma: no cover
        logger.error("PostgreSQL connection failed: %s", exc)
        return f"Connection failed: {exc}"

    try:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
    except Exception as exc:  # pragma: no cover
        logger.error("Query error: %s", exc)
        return f"Query error: {exc}"
    finally:
        conn.close()

    # Format as list-of-dicts JSON-ish string for easy LLM consumption
    result = [dict(zip(colnames, row)) for row in rows]
    return result


postgres_query_tool = StructuredTool(
    name="postgres_query",
    description="Execute a read-only SELECT query against a PostgreSQL database.",
    func=_run_pg_query,
    args_schema=_PGInput,
)
