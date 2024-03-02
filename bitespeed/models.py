from __future__ import annotations

from msgspec import Struct


class IdentifyBody(Struct, rename="camel"):
    email: str | None = None
    phone_number: str | None = None

    def __post_init__(self) -> None:
        if self.email is None and self.phone_number is None:
            raise ValueError("either email or phone number have to be provided")


class Contact(Struct, rename="camel"):
    primary_contact_id: int
    emails: list[str]
    phone_numbers: list[str]
    secondary_contact_ids: list[int]


class IdentifyResponse(Struct, rename="camel"):
    contact: Contact
