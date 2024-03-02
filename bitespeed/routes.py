from __future__ import annotations

from litestar import post

from bitespeed.models import IdentifyBody
from bitespeed.models import IdentifyResponse


@post("/identify")
async def identify(data: IdentifyBody) -> IdentifyResponse:  # noqa: ARG001
    raise NotImplementedError
