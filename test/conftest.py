import attr
import lyft_rides.errors
import pytest

from lyftbutton.lyft import LyftAuth, LyftAccount


@attr.s
class DashButton:
    serial_number = attr.ib()

    def find(self):
        raise NotImplementedError


@pytest.fixture
def environment(monkeypatch):
    monkeypatch.setenv("LYFT_CLIENT_ID", "fakeid")
    monkeypatch.setenv("LYFT_CLIENT_SECRET", "fakesecret")
    monkeypatch.setenv("TOKEN_SECRET", "somesecret")


@pytest.fixture
def jwt(monkeypatch):
    monkeypatch.setattr(
        "jwt.encode",
        lambda payload, secret, algorithm: (
            b"token:%s" % payload["button_id"].encode("utf-8")
        ),
    )


@pytest.fixture
def known_button_id(monkeypatch):
    button_id = "known-button-id"
    button = DashButton(serial_number=button_id)
    lyft_account = LyftAccount(
        id=456, first_name="Jair", last_name="Trejo", has_taken_a_ride=True
    )
    button.lyft_account = lyft_account

    monkeypatch.setattr(
        DashButton, "find", lambda button_id=None, lyft_id=None: button
    )
    monkeypatch.setattr("lyftbutton.api.lyftaccount.DashButton", DashButton)
    monkeypatch.setattr("lyftbutton.api.dashbutton.DashButton", DashButton)

    return button_id


@pytest.fixture
def unknown_button_id(monkeypatch):
    button_id = "unknown-button-id"
    monkeypatch.setattr(
        DashButton, "find", lambda button_id=None, lyft_id=None: None
    )
    monkeypatch.setattr("lyftbutton.api.lyftaccount.DashButton", DashButton)
    monkeypatch.setattr("lyftbutton.api.dashbutton.DashButton", DashButton)
    return button_id


@pytest.fixture
def known_lyft_auth(monkeypatch):
    button_id = "known-button-id"
    button = DashButton(serial_number=button_id)
    lyft_account = LyftAccount(
        id=123, first_name="Jair", last_name="Trejo", has_taken_a_ride=True
    )
    button.lyft_account = lyft_account

    monkeypatch.setattr("lyftbutton.lyft.LyftAuth.lyft_account", lyft_account)
    monkeypatch.setattr(
        DashButton, "find", lambda button_id=None, lyft_id=None: button
    )
    monkeypatch.setattr("lyftbutton.api.lyftaccount.DashButton", DashButton)
    monkeypatch.setattr("lyftbutton.api.dashbutton.DashButton", DashButton)

    return LyftAuth(state="123", code="known")


@pytest.fixture
def unknown_lyft_auth(monkeypatch):
    monkeypatch.setattr(
        "lyftbutton.lyft.LyftAuth.lyft_account",
        LyftAccount(
            id=123, first_name="Jair", last_name="Trejo", has_taken_a_ride=True
        ),
    )
    find = DashButton.find
    monkeypatch.setattr(
        DashButton,
        "find",
        lambda button_id=None, lyft_id=None: None
        if lyft_id
        else find(button_id=button_id),
    )
    monkeypatch.setattr("lyftbutton.api.lyftaccount.DashButton", DashButton)
    monkeypatch.setattr("lyftbutton.api.dashbutton.DashButton", DashButton)

    return LyftAuth(state="123", code="known")


@pytest.fixture
def invalid_lyft_auth(monkeypatch):
    class LyftAuth:
        def __init__(self, state, code):
            pass

        @property
        def lyft_account(self):
            raise lyft_rides.errors.APIError("API error")

    monkeypatch.setattr("lyftbutton.api.lyftaccount.LyftAuth", LyftAuth)

    return LyftAuth(state="unknown", code="invalid")
