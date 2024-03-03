from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from asyncpg import Connection
from asyncpg import connect

from bitespeed import settings


@asynccontextmanager
async def get_connection() -> AsyncGenerator[Connection, None]:
    conn = await connect(settings.DB_URL)
    try:
        yield conn
    finally:
        await conn.close()


async def run_startup_script(conn: Connection) -> None:
    fp = settings.ROOT_DIR / "sql" / "tables.sql"
    script = fp.read_text()

    await conn.execute(script)
