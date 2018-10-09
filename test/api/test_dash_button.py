from lyftbutton.api import (
    get_dash_button, set_dash_button_home, set_dash_button_default_destination)
from lyftbutton.dashbutton import Location


class TestGetDashButton:
    def test_get_unauthenticated(self):
        response = get_dash_button.__wrapped__()

        assert response.status_code == 403

    def test_get_authenticated(self, known_button_id):
        response = get_dash_button.__wrapped__(
            auth_context={'button_id': known_button_id})

        assert response.serial_number == known_button_id


class TestSetDashButtonHome:
    def test_set_unauthenticated(self):
        home = Location(lat=100.2, lng=100.3)

        response = set_dash_button_home.__wrapped__(home)

        assert response.status_code == 403

    def test_set_authenticated(self, known_button_id):
        home = Location(lat=100.2, lng=100.3)

        response = set_dash_button_home.__wrapped__(
            home, auth_context={'button_id': known_button_id})

        assert response.serial_number == known_button_id
        assert response.home.lat == home.lat
        assert response.home.lng == home.lng


class TestSetDashButtonDestination:
    def test_set_unauthenticated(self):
        destination = Location(lat=100.2, lng=100.3)

        response = set_dash_button_default_destination.__wrapped__(destination)

        assert response.status_code == 403

    def test_set_authenticated(self, known_button_id):
        destination = Location(lat=100.2, lng=100.3)

        response = set_dash_button_default_destination.__wrapped__(
            destination, auth_context={'button_id': known_button_id})

        assert response.serial_number == known_button_id
        assert response.destination.lat == destination.lat
        assert response.destination.lng == destination.lng
