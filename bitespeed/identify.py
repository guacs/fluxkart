from __future__ import annotations

from aiosqlite import Connection

from bitespeed.models import Contact
from bitespeed.models import IdentifyBody


class ContactStore:
    def __init__(self, conn: Connection):
        self._conn = conn


class IdentifyService:
    def __init__(self, contact_store: ContactStore):
        self._store = contact_store

    async def identify(self, identify_body: IdentifyBody) -> Contact:
        return Contact(0, [], [], [])


def provide_identify_service(db_conn: Connection) -> IdentifyService:
    return IdentifyService(ContactStore(db_conn))
