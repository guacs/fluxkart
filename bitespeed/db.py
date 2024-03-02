from __future__ import annotations

from collections.abc import AsyncGenerator

from aiosqlite import Connection
from aiosqlite import Cursor
from aiosqlite import connect
from litestar.types.composite_types import Any

from bitespeed import settings


def dict_factory(cursor: Cursor, row: tuple[Any, ...]) -> dict[str, Any]:
    fields = [column[0] for column in cursor.description]
    return dict(zip(fields, row, strict=False))


async def get_connection() -> AsyncGenerator[Connection, None]:
    async with connect(settings.DB_URL, isolation_level=None) as conn:
        conn.row_factory = dict_factory  # type: ignore
        yield conn


async def run_startup_script(conn: Connection) -> None:
    fp = settings.ROOT_DIR / "sql" / "tables.sql"
    script = fp.read_text()

    async with conn.cursor() as cursor:
        await cursor.executescript(script)
