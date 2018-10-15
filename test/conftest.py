import attr
import lyft_rides.errors
import oauth2client.client
import pytest

from lyftbutton.google import GoogleAccount, GoogleAuth
from lyftbutton.lyft import LyftAuth, LyftAccount


@attr.s
class DashButton:
    serial_number = attr.ib()
    google_account = attr.ib(default=None)

    def find(self):
        raise NotImplementedError


@pytest.fixture
def environment(monkeypatch):
    monkeypatch.setenv("TOKEN_SECRET", "somesecret")
    monkeypatch.setenv("LYFT_CLIENT_ID", "lyft:fakeid")
    monkeypatch.setenv("LYFT_CLIENT_SECRET", "lyft:fakesecret")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "google:fakeid")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "google:fakesecret")


@pytest.fixture
def jwt(monkeypatch):
    monkeypatch.setattr(
        "jwt.encode",
        lambda payload, secret, algorithm: (
            b"token:%s" % payload["serial_number"].encode("utf-8")
        ),
    )


@pytest.fixture
def known_serial_number(monkeypatch):
    serial_number = "button:known"
    button = DashButton(serial_number=serial_number)
    lyft_account = LyftAccount(
        id="lyft:123",
        first_name="Jair",
        last_name="Trejo",
        has_taken_a_ride=True,
    )
    button.lyft_account = lyft_account

    monkeypatch.setattr(
        DashButton, "find", lambda serial_number=None, lyft_id=None: button
    )
    monkeypatch.setattr("lyftbutton.api.lyft.DashButton", DashButton)
    monkeypatch.setattr("lyftbutton.api.google.DashButton", DashButton)
    monkeypatch.setattr("lyftbutton.api.dashbutton.DashButton", DashButton)

    return serial_number


@pytest.fixture
def unknown_serial_number(monkeypatch):
    serial_number = "button:unknown"
    monkeypatch.setattr(
        DashButton, "find", lambda serial_number=None, lyft_id=None: None
    )
    monkeypatch.setattr("lyftbutton.api.lyft.DashButton", DashButton)
    monkeypatch.setattr("lyftbutton.api.dashbutton.DashButton", DashButton)
    return serial_number


@pytest.fixture
def known_lyft_auth(monkeypatch):
    serial_number = "button:known"
    button = DashButton(serial_number=serial_number)
    lyft_account = LyftAccount(
        id="lyft:123",
        first_name="Jair",
        last_name="Trejo",
        has_taken_a_ride=True,
    )
    button.lyft_account = lyft_account

    monkeypatch.setattr("lyftbutton.lyft.LyftAuth.account", lyft_account)
    monkeypatch.setattr(
        DashButton, "find", lambda serial_number=None, lyft_id=None: button
    )
    monkeypatch.setattr("lyftbutton.api.lyft.DashButton", DashButton)
    monkeypatch.setattr("lyftbutton.api.dashbutton.DashButton", DashButton)

    return LyftAuth(state="123", code="known")


@pytest.fixture
def unknown_lyft_auth(monkeypatch):
    monkeypatch.setattr(
        "lyftbutton.lyft.LyftAuth.account",
        LyftAccount(
            id="lyft:123",
            first_name="Jair",
            last_name="Trejo",
            has_taken_a_ride=True,
        ),
    )
    find = DashButton.find
    monkeypatch.setattr(
        DashButton,
        "find",
        lambda serial_number=None, lyft_id=None: None
        if lyft_id
        else find(serial_number=serial_number),
    )
    monkeypatch.setattr("lyftbutton.api.lyft.DashButton", DashButton)
    monkeypatch.setattr("lyftbutton.api.dashbutton.DashButton", DashButton)

    return LyftAuth(state="123", code="known")


@pytest.fixture
def invalid_lyft_auth(monkeypatch):
    class LyftAuth:
        def __init__(self, state, code):
            pass

        @property
        def account(self):
            raise lyft_rides.errors.APIError("API error")

    monkeypatch.setattr("lyftbutton.api.lyft.LyftAuth", LyftAuth)

    return LyftAuth(state="unknown", code="invalid")


@pytest.fixture
def known_google_account(monkeypatch, known_serial_number):
    button = DashButton.find(known_serial_number)
    button.google_account = GoogleAccount(calendar="My Google Calendar")

    monkeypatch.setattr("lyftbutton.api.google.DashButton", DashButton)

    return button.google_account


@pytest.fixture
def google_auth(monkeypatch):
    monkeypatch.setattr(
        "lyftbutton.google.GoogleAuth.account",
        GoogleAccount(calendar="My Google Calendar"),
    )

    return GoogleAuth(code="google:code")


@pytest.fixture
def invalid_google_auth(monkeypatch):
    class GoogleAuth:
        def __init__(self, code=None):
            pass

        @property
        def account(self):
            raise oauth2client.client.FlowExchangeError

    return GoogleAuth(code="google:code")
