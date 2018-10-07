from lyftbutton.api import get_dash_button


class TestGetDashButton:
    def test_get_unauthenticated(self, unknown_button_id):
        response = get_dash_button.__wrapped__(None)

        assert response.status_code == 403

    def test_get_authenticated(self, known_button_id):
        response = get_dash_button.__wrapped__(
            auth_context={'button_id': known_button_id})

        assert response.serial_number == known_button_id
