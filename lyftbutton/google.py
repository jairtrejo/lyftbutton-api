"""
Utilities to authenticate with Google and obtain user credentials.
"""
import os
import json
import httplib2
from decimal import Decimal

import attr
import apiclient.discovery
from oauth2client.client import Credentials, OAuth2WebServerFlow


def _get_auth_flow():
    """
    Build an auth flow with the environment credentials.

    :returns: An authentication flow.
    :rtype: :py:class:`oauth2client.client.OAuth2WebServerFlow`
    """
    return OAuth2WebServerFlow(
        client_id=os.environ.get("GOOGLE_CLIENT_ID"),
        client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
        scope="https://www.googleapis.com/auth/calendar.readonly",
        redirect_uri="https://lyftbutton.com/google",
        prompt="consent",
    )


@attr.s
class GoogleAccount:
    """
    A representation of the user's linked Google Account.
    """

    calendar = attr.ib()

    @classmethod
    def from_credentials(cls, credential_data):
        """
        Get a GoogleAccount for the user with the provided credentials.

        :param type cls: The GoogleAccount class.
        :param dict credential_data: Serialized OAuth2 credential.

        :return: The GoogleAccount of the authorized user.
        :rtype: :py:class:`GoogleAccount`
        """
        credentials = Credentials.new_from_json(
            json.dumps(
                credential_data,
                default=lambda obj: int(obj)
                if isinstance(obj, Decimal)
                else obj,
            )
        )
        service = apiclient.discovery.build(
            "calendar",
            "v3",
            http=credentials.authorize(httplib2.Http()),
            cache_discovery=False,
        )

        calendar = service.calendarList().get(calendarId="primary").execute()

        account = cls(calendar=calendar["summary"])
        account.credentials = credential_data

        return account

    def asdict(self):
        return attr.asdict(self)


@attr.s
class GoogleAuth:
    """
    A container for the authentication code provided in the oauth callback.
    """

    code = attr.ib()

    @property
    def account(self):
        """
        Get a google account by authenticating and obtaining credentials.

        :param self: The :py:class:`GoogleAuth` instance.
        :type self: :py:class:`GoogleAuth`

        :return: The authenticated GoogleAccount.
        :rtype: :py:class:`GoogleAccount`
        """
        auth_flow = _get_auth_flow()
        credentials = auth_flow.step2_exchange(self.code)

        return GoogleAccount.from_credentials(
            json.loads(credentials.to_json())
        )

    @staticmethod
    def get_url():
        """
        Get a URL for OAuth redirection.

        :return: A URL
        :rtype: str
        """
        auth_flow = _get_auth_flow()
        return auth_flow.step1_get_authorize_url()
