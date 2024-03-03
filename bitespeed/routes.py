from __future__ import annotations

from asyncpg import Connection
from litestar import post
from litestar.di import Provide
from litestar.params import Dependency

from bitespeed.identify import ContactStore
from bitespeed.identify import IdentifyService
from bitespeed.models import IdentifyBody
from bitespeed.models import IdentifyResponse


def provide_identify_service(db_conn: Connection = Dependency(skip_validation=True)) -> IdentifyService:
    return IdentifyService(ContactStore(db_conn))


@post("/identify", dependencies={"identifier": Provide(provide_identify_service, sync_to_thread=False)})
async def identify(data: IdentifyBody, identifier: IdentifyService) -> IdentifyResponse:
    contact = await identifier.identify(data)

    return IdentifyResponse(contact)
