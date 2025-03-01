import os
from datetime import datetime, timedelta
from time import time

import attr
import jwt
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

    @property
    def token(self):
        return jwt.encode(
            {
                "lyft_id": self.id,
                "exp": datetime.utcnow() + timedelta(hours=1),
            },
            os.environ.get("TOKEN_SECRET"),
            algorithm="HS256",
        ).decode("utf-8")

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

        profile = client.get_user_profile().json

        return cls(
            id=profile["id"],
            first_name=profile["first_name"],
            last_name=profile["last_name"],
            has_taken_a_ride=profile["has_taken_a_ride"],
            credentials=_credentials_to_dict(client.session.oauth2credential),
        )

    def asdict(self):
        account_data = attr.asdict(
            self, filter=lambda attr, value: attr.name != "credentials"
        )

        account_data["token"] = self.token

        return account_data


@attr.s
class LyftAuth:
    state = attr.ib()
    code = attr.ib()

    @property
    def account(self):
        auth_flow = _get_auth_flow()
        url = "url?code={code}&state={state}".format(
            code=self.code, state=self.state
        )
        session = auth_flow.get_session(url)

        return LyftAccount.from_credentials(
            _credentials_to_dict(session.oauth2credential)
        )

    @staticmethod
    def get_url():
        auth_flow = _get_auth_flow()
        return auth_flow.get_authorization_url()
