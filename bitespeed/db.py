from __future__ import annotations

from collections.abc import AsyncGenerator

from aiosqlite import Connection
from aiosqlite import connect

from bitespeed import settings


async def get_connection() -> AsyncGenerator[Connection, None]:
    async with connect(settings.DB_URL, isolation_level=None) as conn:
        yield conn
