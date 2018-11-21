import json
from unittest.mock import MagicMock, PropertyMock, patch

import lyft_rides.errors
import pytest

from lyftbutton.api import create_lyft_account, get_lyft_account


@pytest.mark.usefixtures("environment")
class TestGetLyftAccount:
    @patch("lyftbutton.api.lyft.LyftAuth")
    def test_get_unauthenticated(self, MockLyftAuth):
        MockLyftAuth.get_url.return_value = "some-url"
        response = get_lyft_account.__wrapped__()

        assert response.status_code == 404
        assert json.loads(response.body)["url"] == "some-url"

    @patch("lyftbutton.api.lyft.LyftButton")
    def test_get_authenticated(self, MockLyftButton):
        button = MockLyftButton.find.return_value
        button.lyft_account.asdict.return_value = {
            "id": "lyft:123",
            "token": "secret-token",
        }

        response = get_lyft_account.__wrapped__(
            auth_context={"lyft_id": "lyft:123"}
        )

        assert response["id"] == "lyft:123"
        assert "token" not in response


@pytest.mark.usefixtures("environment")
class TestCreateLyftAccount:
    @patch("lyftbutton.lyft.jwt")
    @patch("lyftbutton.api.lyft.LyftAuth")
    @patch("lyftbutton.api.lyft.LyftButton")
    def test_login_with_an_existing_account(
        self, MockLyftButton, MockLyftAuth, MockJWT
    ):
        MockLyftAuth.return_value.account.id = "lyft:123"
        MockJWT.encode.return_value = "some-token".encode("utf-8")
        MockLyftAuth.return_value.account.asdict.return_value = {
            "some": "json"
        }

        response = create_lyft_account.__wrapped__(MockLyftAuth.return_value)

        assert response.id == "lyft:123"
        MockLyftButton.find.assert_called_once_with(lyft_id="lyft:123")

    @patch("lyftbutton.lyft.jwt")
    @patch("lyftbutton.api.lyft.LyftAuth")
    @patch("lyftbutton.api.lyft.LyftButton")
    def test_login_with_a_new_account(
        self, MockLyftButton, MockLyftAuth, MockJWT
    ):
        MockLyftButton.find.return_value = None
        MockJWT.encode.return_value = "some-token".encode("utf-8")
        MockLyftAuth.return_value.account.id = "lyft:123"

        response = create_lyft_account.__wrapped__(MockLyftAuth.return_value)

        assert response.id == "lyft:123"
        assert (
            MockLyftButton.return_value.lyft_account
            == MockLyftAuth.return_value.account
        )

    @patch("lyftbutton.api.lyft.LyftAuth")
    def test_login_with_an_invalid_state_or_code(self, MockLyftAuth):
        type(MockLyftAuth.return_value).account = PropertyMock(
            side_effect=lyft_rides.errors.APIError
        )
        response = create_lyft_account.__wrapped__(MockLyftAuth.return_value)
        assert response.status_code == 403

    @patch("lyftbutton.lyft.jwt")
    @patch("lyftbutton.api.lyft.LyftAuth")
    @patch("lyftbutton.api.lyft.LyftButton")
    def test_change_lyft_account_for_logged_in_button(
        self, MockLyftButton, MockLyftAuth, MockJWT
    ):
        logged_in_button = MagicMock()

        def find(lyft_id=None):
            if lyft_id == "lyft:123":
                return logged_in_button
            else:
                return None

        MockLyftButton.find.side_effect = find
        logged_in_button.lyft_account.id = "lyft:123"
        MockLyftAuth.return_value.account.id = "lyft:456"
        MockJWT.encode.return_value = "some-token".encode("utf-8")
        MockLyftAuth.return_value.account.asdict.return_value = {
            "some": "json"
        }

        response = create_lyft_account.__wrapped__(
            MockLyftAuth.return_value, auth_context={"lyft_id": "lyft:123"}
        )

        assert response.id == "lyft:456"
        assert logged_in_button.lyft_account.id == "lyft:456"

    @patch("lyftbutton.lyft.jwt")
    @patch("lyftbutton.api.lyft.LyftAuth")
    @patch("lyftbutton.api.lyft.LyftButton")
    def test_claim_a_button_that_belongs_to_someone_else(
        self, MockLyftButton, MockLyftAuth, MockJWT
    ):
        logged_in_button = MagicMock()
        existing_button = MagicMock()

        def find(lyft_id=None):
            if lyft_id == "lyft:123":
                return logged_in_button
            elif lyft_id == "lyft:456":
                return existing_button
            else:
                return None

        MockLyftButton.find.side_effect = find
        logged_in_button.lyft_account.id = "lyft:123"
        MockLyftAuth.return_value.account.id = "lyft:456"
        MockJWT.encode.return_value = "some-token".encode("utf-8")
        MockLyftAuth.return_value.account.asdict.return_value = {
            "some": "json"
        }

        response = create_lyft_account.__wrapped__(
            MockLyftAuth.return_value, auth_context={"lyft_id": "lyft:123"}
        )

        assert response.status_code == 403
        assert logged_in_button.lyft_account.id == "lyft:123"
