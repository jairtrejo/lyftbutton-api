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

    def test_get_authenticated(self, known_button_id, known_lyft_auth):
        response = get_lyft_account.__wrapped__(
            auth_context={"button_id": known_button_id}
        )

        assert type(response) is LyftAccount


@pytest.mark.usefixtures("environment", "jwt")
class TestCreateLyftAccount:
    def test_login_with_an_existing_button(
        self, known_lyft_auth, known_button_id
    ):
        response = create_lyft_account.__wrapped__(known_lyft_auth)

        assert response.status_code == 200
        assert response.headers["Set-Cookie"] == "Token=token:button:known"

    def test_login_with_a_new_button(
        self, unknown_lyft_auth, unknown_button_id
    ):
        response = create_lyft_account.__wrapped__(
            unknown_lyft_auth, button_id=unknown_button_id
        )

        assert response.status_code == 200
        assert response.headers["Set-Cookie"] == "Token=token:button:unknown"

    def test_change_lyft_account_for_logged_in_button(
        self, unknown_lyft_auth, known_button_id
    ):
        response = create_lyft_account.__wrapped__(
            unknown_lyft_auth,
            button_id=known_button_id,
            auth_context={"button_id": known_button_id},
        )

        assert response.status_code == 200
        assert "id" in json.loads(response.body)

    def test_login_with_an_invalid_state_or_code(self, invalid_lyft_auth):
        response = create_lyft_account.__wrapped__(invalid_lyft_auth)
        assert response.status_code == 403

    def test_claim_a_button_that_belongs_to_someone_else(
        self, known_button_id, unknown_lyft_auth
    ):
        response = create_lyft_account.__wrapped__(
            unknown_lyft_auth, button_id=known_button_id
        )

        assert response == Response(status_code=403, body=None, headers={})
