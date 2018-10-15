import json

import pytest

from lyftbutton.api import create_lyft_account, get_lyft_account
from lyftbutton.utils.lambdafn import Response
from lyftbutton.lyft import LyftAccount


@pytest.mark.usefixtures("environment")
class TestGetLyftAccount:
    def test_get_unauthenticated(self):
        response = get_lyft_account.__wrapped__()

        assert response.status_code == 404
        assert "url" in json.loads(response.body)

    def test_get_authenticated(self, known_serial_number, known_lyft_auth):
        response = get_lyft_account.__wrapped__(
            auth_context={"serial_number": known_serial_number}
        )

        assert type(response) is LyftAccount


@pytest.mark.usefixtures("environment", "jwt")
class TestCreateLyftAccount:
    def test_login_with_an_existing_button(
        self, known_lyft_auth, known_serial_number
    ):
        response = create_lyft_account.__wrapped__(known_lyft_auth)

        assert response.status_code == 200
        assert response.headers["Set-Cookie"] == "Token=token:button:known"

    def test_login_with_a_new_button(
        self, unknown_lyft_auth, unknown_serial_number
    ):
        response = create_lyft_account.__wrapped__(
            unknown_lyft_auth, serial_number=unknown_serial_number
        )

        assert response.status_code == 200
        assert response.headers["Set-Cookie"] == "Token=token:button:unknown"

    def test_change_lyft_account_for_logged_in_button(
        self, unknown_lyft_auth, known_serial_number
    ):
        response = create_lyft_account.__wrapped__(
            unknown_lyft_auth,
            serial_number=known_serial_number,
            auth_context={"serial_number": known_serial_number},
        )

        assert response.status_code == 200
        assert "id" in json.loads(response.body)

    def test_login_with_an_invalid_state_or_code(self, invalid_lyft_auth):
        response = create_lyft_account.__wrapped__(invalid_lyft_auth)
        assert response.status_code == 403

    def test_claim_a_button_that_belongs_to_someone_else(
        self, known_serial_number, unknown_lyft_auth
    ):
        response = create_lyft_account.__wrapped__(
            unknown_lyft_auth, serial_number=known_serial_number
        )

        assert response == Response(status_code=403, body=None, headers={})
