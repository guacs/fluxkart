from __future__ import annotations

from litestar import Litestar


def create_app() -> Litestar:
    from bitespeed.routes import identify

    return Litestar([identify])
