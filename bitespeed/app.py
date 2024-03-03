from __future__ import annotations

from collections.abc import AsyncIterable
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from asyncpg import Connection
from litestar import Litestar
from litestar.testing.client.sync_client import Sequence
from litestar.types.composite_types import Dependencies

from bitespeed.db import get_connection
from bitespeed.db import run_startup_script


async def provide_db_conn() -> AsyncIterable[Connection]:
    async with get_connection() as conn:
        yield conn


def create_app(
    override_dependencies: Dependencies | None = None,
    lifespan: Sequence[Callable[[Litestar], AbstractAsyncContextManager]] | None = None,
) -> Litestar:
    from bitespeed.routes import identify

    dependencies: Dependencies = {"db_conn": provide_db_conn}
    if override_dependencies:
        dependencies.update(override_dependencies)

    return Litestar([identify], dependencies=dependencies, debug=True, on_startup=[on_startup], lifespan=lifespan)


async def on_startup(_: Litestar) -> None:
    async with get_connection() as conn:
        await run_startup_script(conn)
