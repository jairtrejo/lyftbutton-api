import json
import os

import attr
import lyft_rides.errors
from lyft_rides.auth import AuthorizationCodeGrant
from lyft_rides.client import LyftRidesClient
from lyft_rides.session import Session

from lyftbutton.credentials import Credentials
from lyftbutton.utils.lambdafn import api_handler, Response
from lyftbutton.models import LyftAccount, LyftAuth
from lyftbutton.tokens import Token


@api_handler
def get_lyft_account(auth_context=None):
    """
    Get the authenticated user's Lyft account

    If the user is not authenticated, returns a URL wich can be used to
    initiate an OAuth flow.

    Args:
        auth_context (str): Authentication context provided by authorizer.
        auth_context.button_id (str): User's button id

    Returns:
        (:class:`LyftAccount`) If the user is authenticated, the Lyft account.
    """
    CLIENT_ID = os.environ.get('LYFT_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('LYFT_CLIENT_SECRET')

    if auth_context is None:
        auth_flow = AuthorizationCodeGrant(
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
            scopes={'profile', 'rides.request', 'offline'},
            state_token='fixed', is_sandbox_mode=False)

        return Response(
            status_code=404,
            body=json.dumps({'url': auth_flow.get_authorization_url()}))

    button_id = auth_context['button_id']
    session = Session(Credentials(button_id).lyft)
    Credentials(button_id).lyft = session.oauth2credential

    client = LyftRidesClient(session)
    user_profile = client.get_user_profile().json

    return LyftAccount(**user_profile)


@api_handler(model=LyftAuth)
def create_lyft_account(lyft_auth, button_id=None, auth_context=None):
    """
    Register a new Lyft account for the authenticated user

    Args:
        lyft_auth (:class:`LyftAuth`) Lyft postback info.
        button_id (str) Button id the user is trying to associate with the
        lyft account.
        auth_context (str): Authentication context provided by authorizer.
        auth_context.button_id (str): User's button id

    Returns:
        (:class:`LyftAccount`) The Lyft account.
    """
    CLIENT_ID = os.environ.get('LYFT_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('LYFT_CLIENT_SECRET')

    auth_flow = AuthorizationCodeGrant(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
        scopes={'profile', 'rides.request', 'offline'},
        state_token='fixed', is_sandbox_mode=False)

    try:
        url = 'url?code={code}&state={state}'.format(
            code=lyft_auth.code, state=lyft_auth.state)
        session = auth_flow.get_session(url)
    except lyft_rides.errors.APIError as e:
        print(e)
        return Response(status_code=403, body='{"message": "%s"}' % e)

    client = LyftRidesClient(session)
    user_profile = client.get_user_profile().json
    lyft_account = LyftAccount(**user_profile)

    token = Token(lyft_account)
    is_button_owner = (
        auth_context and token.button_id
        and token.button_id == auth_context['button_id'])

    if token.button_id and not button_id:
        return Response(status_code=202).set_cookie('Token', token.jwt)

    elif button_id and (not token.button_id or is_button_owner):
        token.button_id = button_id
        Credentials(button_id).lyft = session.oauth2credential

        return Response(
            status_code=200, body=json.dumps(attr.asdict(lyft_account))
        ).set_cookie('Token', token.jwt)

    else:
        return Response(status_code=403)
