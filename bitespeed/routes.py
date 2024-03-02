from __future__ import annotations

from litestar import post
from litestar.di import Provide

from bitespeed.identify import IdentifyService
from bitespeed.identify import provide_identify_service
from bitespeed.models import IdentifyBody
from bitespeed.models import IdentifyResponse


@post("/identify", dependencies={"identifier": Provide(provide_identify_service, sync_to_thread=False)})
async def identify(data: IdentifyBody, identifier: IdentifyService) -> IdentifyResponse:
    contact = await identifier.identify(data)

    return IdentifyResponse(contact)
