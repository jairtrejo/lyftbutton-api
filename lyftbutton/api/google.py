import json

import oauth2client.client

from lyftbutton.dashbutton import DashButton
from lyftbutton.google import GoogleAuth
from lyftbutton.utils.lambdafn import api_handler, Response


@api_handler
def get_google_account(auth_context=None):
    if not auth_context:
        return Response(status_code=403)

    button = DashButton.find(serial_number=auth_context["serial_number"])

    if button.google_account:
        return button.google_account
    else:
        return Response(
            status_code=404, body=json.dumps({"url": GoogleAuth.get_url()})
        )


@api_handler(model=GoogleAuth)
def set_google_account(google_auth, auth_context):
    button = DashButton.find(serial_number=auth_context["serial_number"])

    try:
        button.google_account = google_auth.account
    except oauth2client.client.FlowExchangeError:
        return Response(status_code=403)

    return button.google_account


@api_handler
def delete_google_account(auth_context):
    button = DashButton.find(serial_number=auth_context["serial_number"])
    button.google_account = None

    return Response(status_code=204)
