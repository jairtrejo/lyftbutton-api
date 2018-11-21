import json

import lyft_rides.errors
import structlog

from lyftbutton.lyft import LyftAuth
from lyftbutton.repository import LyftButton
from lyftbutton.utils.lambdafn import Response, api_handler

logger = structlog.get_logger(__name__)


@api_handler
def get_lyft_account(auth_context=None):
    """
    Get the authenticated user's Lyft account

    If the user is not authenticated, returns a URL wich can be used to
    initiate an OAuth flow.

    Args:
        auth_context (str): Authentication context provided by authorizer.
        auth_context.lyft_id (str): User's button id

    Returns:
        (:class:`LyftAccount`) If the user is authenticated, the Lyft account.
    """
    if auth_context is None:
        return Response(
            status_code=404, body=json.dumps({"url": LyftAuth.get_url()})
        )

    btn = LyftButton.find(lyft_id=auth_context["lyft_id"])
    account = getattr(btn, "lyft_account", None)

    if account:
        account = account.asdict()
        # Scrub authentication token
        del account["token"]

    return account


@api_handler(model=LyftAuth)
def create_lyft_account(lyft_auth, auth_context=None):
    """
    Register a new Lyft account

    Args:
        lyft_auth (:class:`LyftAuth`) Lyft postback info.
        auth_context (dict): Authentication context provided by authorizer.
        auth_context.lyft_id (str): User's lyft account id

    Returns:
        (:class:`LyftAccount`) The Lyft account.
    """
    try:
        lyft_account = lyft_auth.account
    except lyft_rides.errors.APIError as e:
        logger.error("Lyft API Error", exc_info=e)
        return Response(status_code=403, body='{"message": "%s"}' % e)

    existing_btn = LyftButton.find(lyft_id=lyft_account.id)

    if auth_context and not existing_btn:
        auth_btn = LyftButton.find(lyft_id=auth_context["lyft_id"])
    elif auth_context and existing_btn:
        return Response(status_code=403)
    else:
        auth_btn = None

    btn = auth_btn or existing_btn or LyftButton(lyft_id=lyft_account.id)

    btn.lyft_account = lyft_account

    return lyft_account
