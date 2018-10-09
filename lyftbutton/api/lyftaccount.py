import json
import os

import jwt
import lyft_rides.errors

from lyftbutton.utils.lambdafn import api_handler, Response
from lyftbutton.lyft import LyftAuth
from lyftbutton.dashbutton import DashButton


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
    if auth_context is None:
        return Response(
            status_code=404,
            body=json.dumps({'url': LyftAuth.get_url()}))

    btn = DashButton.find(button_id=auth_context['button_id'])
    return getattr(btn, 'lyft_account', None)


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
    try:
        lyft_account = lyft_auth.lyft_account
    except lyft_rides.errors.APIError as e:
        return Response(status_code=403, body='{"message": "%s"}' % e)

    if auth_context:
        btn = DashButton.find(button_id=auth_context['button_id'])
    elif button_id and not DashButton.find(button_id=button_id):
        btn = DashButton(serial_number=button_id)
    else:
        btn = DashButton.find(lyft_id=lyft_account.id)

    if btn:
        btn.lyft_account = lyft_account

        body = json.dumps(lyft_account.asdict())

        response = Response(status_code=200, body=body)

        if not auth_context:
            TOKEN_SECRET = os.environ.get('TOKEN_SECRET')
            token = jwt.encode(
                {'button_id': btn.serial_number},
                TOKEN_SECRET,
                algorithm='HS256'
            ).decode('utf-8')

            response = response.set_cookie('Token', token)

        return response

    else:
        return Response(status_code=403)
