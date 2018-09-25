import json
import os

from lyft_rides.auth import AuthorizationCodeGrant
from lyft_rides.client import LyftRidesClient
from lyft_rides.session import Session

from .credentials import Credentials
from .lambdautils import api_handler, Response
from .models import LyftAccount, LyftAuth


@api_handler
def get_lyft_account(auth_context=None):
    """
    Get the authenticated user's Lyft account

    If the user is not authenticated, returns a URL wich can be used to
    initiate an OAuth flow.

    Args:
        auth_context (str): Authentication context provided by authorizer.

    Returns:
        (:class:`LyftAccount`) If the user is authenticated, the Lyft account.
    """
    CLIENT_ID = os.environ.get('LYFT_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('LYFT_CLIENT_SECRET')

    if auth_context is None:
        auth_flow = AuthorizationCodeGrant(
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
            scopes=['profile', 'rides.request', 'offline'],
            state_token='fixed')

        return Response(
            status_code=404,
            body=json.dumps({'error': auth_flow.get_authorization_url()}))

    button_id = auth_context['button_id']
    session = Session(Credentials(button_id).lyft)
    client = LyftRidesClient(session)
    user_profile = client.get_user_profile().json()

    return LyftAccount(**user_profile)


@api_handler(model=LyftAuth)
def create_lyft_account(lyft_auth, auth_context, button_id=None):
    """
    Register a new Lyft account for the authenticated user

    Args:
        lyft_auth (:class:`LyftAuth`) Lyft postback info.

    Returns:
        (:class:`LyftAccount`) The Lyft account.
    """
    CLIENT_ID = os.environ.get('LYFT_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('LYFT_CLIENT_SECRET')

    auth_flow = AuthorizationCodeGrant(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
        scopes=['profile', 'rides.request', 'offline'], state_token='fixed')

    session = auth_flow.get_session(
        'url?code={code}&state={state}'.format(
            code=lyft_auth.code, state=lyft_auth.state))

    button_id = button_id or auth_context['button_id']
    Credentials(button_id).lyft = session.oauth2credential
    client = LyftRidesClient(session)
    user_profile = client.get_user_profile().json()

    return LyftAccount(**user_profile)
