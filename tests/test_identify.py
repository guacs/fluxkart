from __future__ import annotations

from typing import Any

import pytest
from litestar.testing import TestClient

from bitespeed.app import create_app

URL = "/identify"


def create_body(phone_number: str | None, email: str | None) -> dict[str, str | None]:
    return {"phoneNumber": phone_number, "email": email}


def assert_reponse_bodies_are_equal(actual: dict[str, Any], expected: dict[str, Any]) -> None:
    actual, expected = actual["contact"], expected["contact"]

    assert actual["primaryContactId"] == expected["primaryContactId"], "primary contact ID differs"

    assert actual["emails"][0] == expected["emails"][0], "primary emails differs"
    assert sorted(actual["emails"][1:]) == sorted(expected["emails"][1:]), "secondary emails differ"

    assert actual["phoneNumbers"][0] == expected["phoneNumbers"][0], "primary phone numbers differs"
    assert sorted(actual["phoneNumbers"][1:]) == sorted(expected["phoneNumbers"][1:]), "secondary phone numers differ"

    assert sorted(actual["secondaryContactIds"]) == sorted(
        expected["secondaryContactIds"]
    ), "secondary contact ids differ"


@pytest.fixture()
def test_client() -> TestClient:
    app = create_app()

    return TestClient(app)


def test_new_contact_created(test_client: TestClient) -> None:
    body = create_body("123456", "itachi@uchiha.com")
    response = test_client.post(URL, json=body)

    assert response.is_success
    expected_response_body = {
        "contact": {
            "primaryContactId": 1,
            "emails": ["itachi@uchiha.com"],
            "phoneNumbers": ["123456"],
            "secondaryContactIds": [],
        }
    }
    assert_reponse_bodies_are_equal(response.json(), expected_response_body)


@pytest.mark.parametrize(
    "body",
    [
        create_body("123456", "itachi@uchiha.com"),
        create_body("123456", "itachi@konoha.com"),
        create_body("123456", None),
        create_body(None, "itachi@uchiha.com"),
        create_body(None, "itachi@konoha.com"),
    ],
)
def test_contacts_linked_with_phone_number(test_client: TestClient, body: dict[str, str | None]) -> None:
    response = test_client.post(URL, json=create_body("123456", "itachi@uchiha.com"))
    assert response.is_success

    response = test_client.post(URL, json=create_body("123456", "itachi@konoha.com"))
    assert response.is_success

    response = test_client.post(URL, json=body)
    expected_response_body = {
        "contact": {
            "primaryContactId": 1,
            "emails": ["itachi@uchiha.com", "itachi@konoha.com"],
            "phoneNumbers": ["123456"],
            "secondaryContactIds": [],
        }
    }

    assert response.is_success
    assert_reponse_bodies_are_equal(response.json(), expected_response_body)


@pytest.mark.parametrize(
    "body",
    [
        create_body("123456", "itachi@uchiha.com"),
        create_body("345678", "itachi@uchiha.com"),
        create_body("123456", None),
        create_body("345678", None),
        create_body(None, "itachi@uchiha.com"),
    ],
)
def test_contacts_linked_with_email(test_client: TestClient, body: dict[str, str | None]) -> None:
    response = test_client.post(URL, json=create_body("123456", "itachi@uchiha.com"))
    assert response.is_success

    response = test_client.post(URL, json=create_body("345678", "itachi@uchiha.com"))
    assert response.is_success

    response = test_client.post(URL, json=body)
    expected_response_body = {
        "contact": {
            "primaryContactId": 1,
            "emails": ["itachi@uchiha.com", "itachi@konoha.com"],
            "phoneNumbers": ["123456"],
            "secondaryContactIds": [],
        }
    }

    assert response.is_success
    assert_reponse_bodies_are_equal(response.json(), expected_response_body)
