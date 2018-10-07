import os

import attr
from lyft_rides.auth import AuthorizationCodeGrant
from lyft_rides.client import LyftRidesClient
from lyft_rides.session import Session


def _get_auth_flow():
    CLIENT_ID = os.environ.get('LYFT_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('LYFT_CLIENT_SECRET')

    auth_flow = AuthorizationCodeGrant(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
        scopes={'profile', 'rides.request', 'offline'},
        state_token='fixed', is_sandbox_mode=False)

    return auth_flow


@attr.s
class LyftAccount:
    id = attr.ib()
    first_name = attr.ib()
    last_name = attr.ib()
    has_taken_a_ride = attr.ib()

    @classmethod
    def from_credentials(cls, oauth2credential):
        session = Session(oauth2credential)
        client = LyftRidesClient(session)
        return LyftAccount(**client.get_user_profile().json)


@attr.s
class LyftAuth:
    state = attr.ib()
    code = attr.ib()

    @property
    def lyft_account(self):
        auth_flow = _get_auth_flow()
        url = 'url?code={code}&state={state}'.format(
            code=self.code, state=self.state)
        session = auth_flow.get_session(url)
        return LyftAccount.from_credentials(session.oauth2credential)

    @classmethod
    def get_url(self):
        auth_flow = _get_auth_flow()
        return auth_flow.get_authorization_url()
