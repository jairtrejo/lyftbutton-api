import json

import pytest
from lyft_rides.session import Session

from lyftbutton import get_lyft_account, create_lyft_account
from lyftbutton.models import LyftAuth


class FakeResponse:
    def __init__(self, json):
        self._json = json

    def json(self):
        return self._json


@pytest.fixture
def environment(monkeypatch):
    monkeypatch.setenv('LYFT_CLIENT_ID', 'fakeid')
    monkeypatch.setenv('LYFT_CLIENT_SECRET', 'fakesecret')


@pytest.fixture
def user_profile(monkeypatch):
    profile = {
        'id': 'some-id'
    }

    monkeypatch.setattr(
        'lyft_rides.client.LyftRidesClient.get_user_profile',
        lambda _: FakeResponse(profile))

    return profile


@pytest.mark.usefixtures('environment')
class TestGetLyftAccount:
    def test_unauthenticated_returns_oauth_url(self, monkeypatch):
        monkeypatch.setattr(
            'lyft_rides.auth.AuthorizationCodeGrant.get_authorization_url',
            lambda _: 'some-auth-url.com')

        response = get_lyft_account.__wrapped__()

        assert response.status_code == 404
        assert json.loads(response.body)['error'] == 'some-auth-url.com'

    def test_authenticated_returns_account(self, monkeypatch, user_profile):
        auth_context = {'button_id': '123'}

        account = get_lyft_account.__wrapped__(auth_context=auth_context)

        assert account.id == user_profile['id']


@pytest.mark.usefixtures('environment')
class TestCreateLyftAccount:
    def test_valid_lyft_code_returns_account(self, monkeypatch, user_profile):
        monkeypatch.setattr(
            'lyft_rides.auth.AuthorizationCodeGrant.get_session',
            lambda _, __: Session('xyz'))
        lyft_auth = LyftAuth(code='123', state='456')
        auth_context = {'button_id': '123'}

        account = create_lyft_account.__wrapped__(
            lyft_auth, auth_context=auth_context)

        assert account.id == user_profile['id']
