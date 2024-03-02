from __future__ import annotations

from typing import Literal

from msgspec import Struct


class IdentifyBody(Struct, rename="camel"):
    email: str | None = None
    phone_number: str | None = None

    def __post_init__(self) -> None:
        if self.email is None and self.phone_number is None:
            raise ValueError("either email or phone number have to be provided")


LinkPrecedence = Literal["primary", "secondary"]


class NewContact(Struct, kw_only=True):
    phone_number: str | None
    email: str | None
    linked_id: int | None
    link_precedence: LinkPrecedence


class SingleContact(Struct):
    id: int
    phone_number: str | None
    email: str | None
    linked_id: int | None
    link_precedence: LinkPrecedence


class Contact(Struct, rename="camel"):
    primary_contact_id: int
    emails: list[str]
    phone_numbers: list[str]
    secondary_contact_ids: list[int]

    @classmethod
    def from_primary_and_secondary(cls, primary: SingleContact, secondary: list[SingleContact]) -> Contact:
        emails, phone_numbers = [], []
        secondary_ids = []
        if primary.email:
            emails.append(primary.email)

        if primary.phone_number:
            phone_numbers.append(primary.phone_number)

        for contact in secondary:
            if (email := contact.email) and email not in emails:
                emails.append(email)
            if (phone_number := contact.phone_number) and phone_number not in phone_numbers:
                phone_numbers.append(phone_number)
            secondary_ids.append(contact.id)

        return Contact(primary.id, emails=emails, phone_numbers=phone_numbers, secondary_contact_ids=secondary_ids)


class IdentifyResponse(Struct, rename="camel"):
    contact: Contact
