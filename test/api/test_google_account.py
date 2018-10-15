import json

from lyftbutton.api import (
    delete_google_account,
    get_google_account,
    set_google_account,
)


class TestGetGoogleAccount:
    def test_get_unauthenticated(self):
        response = get_google_account.__wrapped__()

        assert response.status_code == 403

    def test_no_account(self, known_button_id):
        auth_context = {"button_id": known_button_id}

        response = get_google_account.__wrapped__(auth_context=auth_context)

        assert response.status_code == 404
        assert "url" in json.loads(response.body)

    def test_authenticated(self, known_button_id, known_google_account):
        auth_context = {"button_id": known_button_id}

        response = get_google_account.__wrapped__(auth_context=auth_context)

        assert response.calendar == known_google_account.calendar


class TestSetGoogleAccount:
    def test_set_account(self, known_button_id, google_auth):
        auth_context = {"button_id": known_button_id}

        response = set_google_account.__wrapped__(
            google_auth, auth_context=auth_context
        )

        assert response.calendar == google_auth.google_account.calendar

    def test_set_invalid_account(self, known_button_id, invalid_google_auth):
        auth_context = {"button_id": known_button_id}

        response = set_google_account.__wrapped__(
            invalid_google_auth, auth_context=auth_context
        )

        assert response.status_code == 403


class TestDeleteGoogleAccount:
    def test_delete_account(self, known_button_id):
        auth_context = {"button_id": known_button_id}

        response = delete_google_account.__wrapped__(auth_context=auth_context)

        assert response.status_code == 204
