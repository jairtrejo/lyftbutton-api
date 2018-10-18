import json

import oauth2client.client

from lyftbutton.google import GoogleAuth
from lyftbutton.repository import LyftButton
from lyftbutton.utils.lambdafn import api_handler, Response


@api_handler
def get_google_account(auth_context=None):
    if not auth_context:
        return Response(status_code=403)

    account = LyftButton.find(lyft_id=auth_context["lyft_id"]).google_account

    if account:
        return account
    else:
        return Response(
            status_code=404, body=json.dumps({"url": GoogleAuth.get_url()})
        )


@api_handler(model=GoogleAuth)
def set_google_account(google_auth, auth_context):
    button = LyftButton.find(lyft_id=auth_context["lyft_id"])

    try:
        button.google_account = google_auth.account
    except oauth2client.client.FlowExchangeError:
        return Response(status_code=403)

    return button.google_account


@api_handler
def delete_google_account(auth_context):
    button = LyftButton.find(lyft_id=auth_context["lyft_id"])
    button.google_account = None

    return Response(status_code=204)
