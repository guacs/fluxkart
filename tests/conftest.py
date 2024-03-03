from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
from asyncpg import Connection
from litestar import Litestar
from litestar.datastructures.state import State
from litestar.di import Provide
from litestar.testing import TestClient
from litestar.types.helper_types import Iterable

from bitespeed.app import create_app
from bitespeed.db import get_connection
from bitespeed.db import run_startup_script


@pytest.fixture()
def test_client() -> Iterable[TestClient]:
    # This is to ensure that we use the same connection throughout the duration of a single test.
    # This allows for "persistence" (not really, since we're in a transaction) across multiple
    # requests from the client.
    @asynccontextmanager
    async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
        async with get_connection() as conn:
            txn = conn.transaction()
            await txn.start()
            try:
                app.state.db_connection = conn
                await conn.execute("DROP TABLE contact")
                await run_startup_script(conn)

                yield
            finally:
                await txn.rollback()

    def get_conn(state: State) -> Connection:
        return state.db_connection

    app = create_app({"db_conn": Provide(get_conn, use_cache=True, sync_to_thread=False)}, [lifespan])

    with TestClient(app) as client:
        yield client
