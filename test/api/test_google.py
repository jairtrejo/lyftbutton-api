import json
from unittest.mock import MagicMock, PropertyMock, patch

import oauth2client.client

from lyftbutton.api import (
    delete_google_account,
    get_google_account,
    set_google_account,
)


class TestGetGoogleAccount:
    def test_get_unauthenticated(self):
        response = get_google_account.__wrapped__()

        assert response.status_code == 403

    @patch("lyftbutton.api.google.LyftButton")
    def test_no_account(self, MockLyftButton):
        MockLyftButton.find.return_value.google_account = None

        response = get_google_account.__wrapped__(
            auth_context={"lyft_id": "lyft:123"}
        )

        assert response.status_code == 404
        assert "url" in json.loads(response.body)

    @patch("lyftbutton.api.google.LyftButton")
    def test_authenticated(self, MockLyftButton):
        MockLyftButton.find.return_value.google_account.calendar = (
            "My Calendar"
        )

        response = get_google_account.__wrapped__(
            auth_context={"lyft_id": "lyft:123"}
        )

        assert response.calendar == "My Calendar"


class TestSetGoogleAccount:
    @patch("lyftbutton.api.google.LyftButton")
    def test_set_account(self, MockLyftButton):
        google_auth = MagicMock()

        response = set_google_account.__wrapped__(
            google_auth, auth_context={"lyft_id": "lyft:123"}
        )

        assert response.calendar == google_auth.account.calendar

    @patch("lyftbutton.api.google.LyftButton")
    def test_set_invalid_account(self, MockLyftButton):
        invalid_google_auth = MagicMock()
        type(invalid_google_auth).account = PropertyMock(
            side_effect=oauth2client.client.FlowExchangeError
        )

        response = set_google_account.__wrapped__(
            invalid_google_auth, auth_context={"lyft_id": "lyft:123"}
        )

        assert response.status_code == 403


class TestDeleteGoogleAccount:
    @patch("lyftbutton.api.google.LyftButton")
    def test_delete_account(self, MockLyftButton):
        button = MockLyftButton.find.return_value

        response = delete_google_account.__wrapped__(
            auth_context={"lyft_id": "lyft:123"}
        )

        assert response.status_code == 204
        assert button.google_account is None
