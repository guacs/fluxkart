from __future__ import annotations

from litestar import Litestar
from litestar.types.composite_types import Dependencies


def create_app() -> Litestar:
    from bitespeed.db import get_connection
    from bitespeed.routes import identify

    dependencies: Dependencies = {"db_conn": get_connection}

    return Litestar([identify], dependencies=dependencies, debug=True)
