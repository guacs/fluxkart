from __future__ import annotations

from litestar import Litestar
from litestar.types.composite_types import Dependencies


def create_app(override_dependencies: Dependencies | None = None) -> Litestar:
    from bitespeed.db import get_connection
    from bitespeed.routes import identify

    dependencies: Dependencies = {"db_conn": get_connection}
    if override_dependencies:
        dependencies.update(override_dependencies)

    return Litestar([identify], dependencies=dependencies, debug=True)
