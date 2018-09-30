import pytest
import lyft_rides.errors
from lyft_rides.session import Session

from lyftbutton.models import LyftAuth


class FakeLyftResponse:
    def __init__(self):
        self.json = {
            'id': 'some-id',
            'first_name': 'Harry',
            'last_name': 'Potter',
            'has_taken_a_ride': True
        }


def make_fake_token(button_id):
    class Token:
        def __init__(self, lyft_account):
            self.button_id = button_id

        @property
        def jwt(self):
            return 'token:%s' % self.button_id

    return Token


def make_fake_credentials(lyft):
    class Credentials:
        def __init__(self, lyft_account):
            self.lyft = lyft

    return Credentials


@pytest.fixture
def environment(monkeypatch):
    monkeypatch.setenv('LYFT_CLIENT_ID', 'fakeid')
    monkeypatch.setenv('LYFT_CLIENT_SECRET', 'fakesecret')
    monkeypatch.setenv('TOKEN_SECRET', 'somesecret')


@pytest.fixture
def jwt(monkeypatch):
    monkeypatch.setattr(
        'jwt.encode',
        lambda payload, secret, algorithm: (
            b'token:%s' % payload['button_id'].encode('utf-8')))


@pytest.fixture
def known_button_id(monkeypatch):
    button_id = 'known-button-id'
    monkeypatch.setattr(
        'lyftbutton.api.lyftaccount.Credentials', make_fake_credentials('xyz'))
    return button_id


@pytest.fixture
def unknown_button_id(monkeypatch):
    button_id = 'unknown-button-id'
    monkeypatch.setattr(
        'lyftbutton.api.lyftaccount.Credentials', make_fake_credentials(None))
    return button_id


@pytest.fixture
def known_lyft_auth(monkeypatch, jwt):
    monkeypatch.setattr(
        'lyft_rides.auth.AuthorizationCodeGrant.get_session',
        lambda self, url: Session('credentials'))

    monkeypatch.setattr(
        'lyft_rides.client.LyftRidesClient.get_user_profile',
        lambda _: FakeLyftResponse())

    monkeypatch.setattr(
        'lyftbutton.api.lyftaccount.Token', make_fake_token('known-button-id'))

    return LyftAuth(state='123', code='known')


@pytest.fixture
def unknown_lyft_auth(monkeypatch, jwt):
    monkeypatch.setattr(
        'lyft_rides.auth.AuthorizationCodeGrant.get_session',
        lambda self, url: Session('credentials'))

    monkeypatch.setattr(
        'lyft_rides.client.LyftRidesClient.get_user_profile',
        lambda _: FakeLyftResponse())

    monkeypatch.setattr(
        'lyftbutton.api.lyftaccount.Token', make_fake_token(None))

    return LyftAuth(state='123', code='unknown')


@pytest.fixture
def invalid_lyft_auth(monkeypatch):
    def fail_get_session(self, url):
        raise lyft_rides.errors.APIError("API error")

    monkeypatch.setattr(
        'lyft_rides.auth.AuthorizationCodeGrant.get_session',
        fail_get_session)

    return LyftAuth(state="unknown", code="invalid")
