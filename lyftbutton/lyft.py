import os
from time import time

import attr
from lyft_rides.auth import AuthorizationCodeGrant
from lyft_rides.client import LyftRidesClient
from lyft_rides.session import OAuth2Credential, Session


def _get_auth_flow():
    auth_flow = AuthorizationCodeGrant(
        client_id=os.environ.get("LYFT_CLIENT_ID"),
        client_secret=os.environ.get("LYFT_CLIENT_SECRET"),
        scopes={"profile", "rides.request", "offline"},
        state_token="fixed",
        is_sandbox_mode=False,
    )

    return auth_flow


def _credentials_to_dict(credentials):
    return {
        "access_token": credentials.access_token,
        "expires_in_seconds": credentials.expires_in_seconds,
        "scopes": list(credentials.scopes),
        "grant_type": credentials.grant_type,
        "refresh_token": credentials.refresh_token,
    }


@attr.s
class LyftAccount:
    id = attr.ib()
    first_name = attr.ib()
    last_name = attr.ib()
    has_taken_a_ride = attr.ib()
    credentials = attr.ib(default=None)

    @classmethod
    def from_credentials(cls, credential_data):
        credential_data["expires_in_seconds"] = (
            int(credential_data["expires_in_seconds"]) - time()
        )
        oauth2credential = OAuth2Credential(
            **credential_data,
            client_id=os.environ.get("LYFT_CLIENT_ID"),
            client_secret=os.environ.get("LYFT_CLIENT_SECRET")
        )
        session = Session(oauth2credential)
        client = LyftRidesClient(session)

        client.refresh_oauth_credential()

        return cls(
            **client.get_user_profile().json,
            credentials=_credentials_to_dict(client.session.oauth2credential)
        )

    def asdict(self):
        return attr.asdict(
            self, filter=lambda attr, value: attr.name != "credentials"
        )


@attr.s
class LyftAuth:
    state = attr.ib()
    code = attr.ib()

    @property
    def lyft_account(self):
        auth_flow = _get_auth_flow()
        url = "url?code={code}&state={state}".format(
            code=self.code, state=self.state
        )
        session = auth_flow.get_session(url)

        return LyftAccount.from_credentials(
            _credentials_to_dict(session.oauth2credential)
        )

    @classmethod
    def get_url(self):
        auth_flow = _get_auth_flow()
        return auth_flow.get_authorization_url()
