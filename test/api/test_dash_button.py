from unittest.mock import patch

from lyftbutton.api import edit_dash_button, get_dash_button
from lyftbutton.dashbutton import DashButton, Location


class TestGetDashButton:
    def test_get_unauthenticated(self):
        response = get_dash_button.__wrapped__()

        assert response.status_code == 403

    @patch("lyftbutton.api.dashbutton.LyftButton")
    def test_get_authenticated(self, MockLyftButton):
        MockLyftButton.find.return_value.dash_button.serial_number = "btn:123"

        response = get_dash_button.__wrapped__(
            auth_context={"lyft_id": "lyft:123"}
        )

        assert response.serial_number == "btn:123"

    @patch("lyftbutton.api.dashbutton.LyftButton")
    def test_no_dash_button(self, MockLyftButton):
        MockLyftButton.find.return_value.dash_button = None

        response = get_dash_button.__wrapped__(
            auth_context={"lyft_id": "lyft:123"}
        )

        assert response is None


class TestEditDashButton:
    def test_edit_unauthenticated(self):
        response = edit_dash_button.__wrapped__(
            DashButton(serial_number="button:123")
        )

        assert response.status_code == 403

    @patch("lyftbutton.api.dashbutton.LyftButton")
    def test_edit_brand_new_button(self, MockLyftButton):
        MockLyftButton.find.return_value.dash_button = None

        response = edit_dash_button.__wrapped__(
            DashButton(serial_number="button:123"),
            auth_context={"lyft_id": "lyft:123"},
        )

        assert response.serial_number == "button:123"
        assert MockLyftButton.find.return_value.dash_button == response

    @patch("lyftbutton.api.dashbutton.LyftButton")
    def test_edit_existing_button(self, MockLyftButton):
        MockLyftButton.find.return_value.dash_button = DashButton(
            serial_number="button:123"
        )

        response = edit_dash_button.__wrapped__(
            DashButton(serial_number="button:456"),
            auth_context={"lyft_id": "lyft:123"},
        )

        assert response.serial_number == "button:456"

    @patch("lyftbutton.api.dashbutton.LyftButton")
    def test_add_field_to_existing_button(self, MockLyftButton):
        MockLyftButton.find.return_value.dash_button = DashButton(
            serial_number="button:123"
        )

        response = edit_dash_button.__wrapped__(
            DashButton(home=Location(lat=120, lng=90)),
            auth_context={"lyft_id": "lyft:123"},
        )

        assert response.serial_number == "button:123"
        assert response.home == Location(lat=120, lng=90)
