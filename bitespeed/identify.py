from __future__ import annotations

from typing import Final

from aiosqlite import Connection
from pypika import Criterion
from pypika import Parameter
from pypika import SQLLiteQuery as Query
from pypika import Table

from bitespeed.models import Contact
from bitespeed.models import IdentifyBody
from bitespeed.models import NewContact
from bitespeed.models import SingleContact


class ContactStore:
    _table: Final[Table] = Table("contact")

    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    async def get_all(self, email: str | None, phone_number: str | None) -> list[SingleContact]:
        if not email and not phone_number:
            raise ValueError("either email or phone number have to be provided")

        all_contacts = self._table.as_("all_contacts")
        contacts = self._table

        filters, parameters = [], []
        if email:
            filters.append(contacts.email == Parameter("?"))
            parameters.append(email)
        if phone_number:
            filters.append(contacts.phone_number == Parameter("?"))
            parameters.append(phone_number)

        query = (
            Query.from_(all_contacts)
            .select(
                all_contacts.id,
                all_contacts.phone_number,
                all_contacts.email,
                all_contacts.linked_id,
                all_contacts.link_precedence,
            )
            .distinct()
            .join(contacts)
            .on(
                (all_contacts.id == contacts.id)
                | (all_contacts.linked_id == contacts.id)
                | (all_contacts.id == contacts.linked_id)
                | (all_contacts.linked_id == contacts.linked_id)
            )
            .where(Criterion.any(filters))
            .orderby(all_contacts.created_at)
            .get_sql()
        )

        async with self._conn.cursor() as cursor:
            await cursor.execute(query, parameters)
            rows = await cursor.fetchall()

            return [SingleContact(**r) for r in rows]

    async def add_new_contact(self, new_contact: NewContact) -> int:
        query = """
INSERT INTO
  contact (phone_number, email, linked_id, link_precedence)
VALUES
  (?, ?, ?, ?) RETURNING id;
        """

        async with self._conn.cursor() as cursor:
            await cursor.execute(
                query, (new_contact.phone_number, new_contact.email, new_contact.linked_id, new_contact.link_precedence)
            )
            row = await cursor.fetchone()

            assert row is not None

            return row["id"]

    async def mark_as_secondary(self, contact_ids: list[int], linked_id: int) -> None:
        table = self._table
        query = (
            Query.update(table)
            .set(table.link_precedence, "secondary")
            .set(table.linked_id, Parameter("?"))
            .where(table.id.isin([Parameter("?") for _ in range(len(contact_ids))]))
            .get_sql()
        )

        async with self._conn.cursor() as cursor:
            await cursor.execute(query, (linked_id, *contact_ids))


class IdentifyService:
    def __init__(self, contact_store: ContactStore) -> None:
        self._store = contact_store

    async def identify(self, identify_body: IdentifyBody) -> Contact:
        contacts = await self._store.get_all(identify_body.email, identify_body.phone_number)
        if not contacts:
            primary = await self._new_primary_contact(identify_body)

            return Contact.from_primary_and_secondary(primary, [])

        primary, secondary = await self._get_primary_contact_and_secondary_contacts(contacts)

        if self._has_new_information(contacts, identify_body):
            new_secondary = await self._new_secondary_contact(identify_body, primary.id)
            secondary.append(new_secondary)

        return Contact.from_primary_and_secondary(primary, secondary)

    def _has_new_information(self, contacts: list[SingleContact], identify_body: IdentifyBody) -> bool:
        found_email, found_phone_number = identify_body.email is None, identify_body.phone_number is None
        for contact in contacts:
            if (email := identify_body.email) and email == contact.email:
                found_email = True
            if (phone_number := identify_body.phone_number) and phone_number == contact.phone_number:
                found_phone_number = True

        return not found_email or not found_phone_number

    async def _get_primary_contact_and_secondary_contacts(
        self,
        contacts: list[SingleContact],
    ) -> tuple[SingleContact, list[SingleContact]]:
        primary: list[SingleContact] = []
        secondary: list[SingleContact] = []
        for contact in contacts:
            if contact.link_precedence == "primary":
                primary.append(contact)
            else:
                secondary.append(contact)

        assert len(primary)
        primary_contact = primary[0]

        if len(primary) > 1:
            # Only the first one is the primary. The rest now become
            # secondary. The first is the primary because it's the one that was created the earliest.
            primary_contact = primary[0]
            secondary_ids = []
            for contact in primary[1:]:
                contact.link_precedence = "secondary"
                contact.linked_id = primary_contact.id

                secondary.append(contact)
                secondary_ids.append(contact.id)

            await self._store.mark_as_secondary(secondary_ids, primary_contact.id)

        return primary_contact, secondary

    async def _new_primary_contact(self, identify_body: IdentifyBody) -> SingleContact:
        new_contact = NewContact(
            phone_number=identify_body.phone_number,
            email=identify_body.email,
            linked_id=None,
            link_precedence="primary",
        )
        contact_id = await self._store.add_new_contact(new_contact)

        return SingleContact(
            contact_id,
            identify_body.phone_number,
            identify_body.email,
            None,
            "primary",
        )

    async def _new_secondary_contact(self, identify_body: IdentifyBody, linked_id: int) -> SingleContact:
        new_contact = NewContact(
            phone_number=identify_body.phone_number,
            email=identify_body.email,
            linked_id=linked_id,
            link_precedence="secondary",
        )
        contact_id = await self._store.add_new_contact(new_contact)

        return SingleContact(
            contact_id,
            identify_body.phone_number,
            identify_body.email,
            linked_id,
            "secondary",
        )


def provide_identify_service(db_conn: Connection) -> IdentifyService:
    return IdentifyService(ContactStore(db_conn))
