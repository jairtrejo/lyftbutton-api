import attr

from lyftbutton.dashbutton import DashButton
from lyftbutton.utils.lambdafn import api_handler, Response
from lyftbutton.repository import LyftButton


@api_handler
def get_dash_button(auth_context=None):
    if not auth_context:
        return Response(status_code=403)

    return LyftButton.find(lyft_id=auth_context["lyft_id"]).dash_button


@api_handler(model=DashButton)
def edit_dash_button(new_button, auth_context=None):
    if not auth_context:
        return Response(status_code=403)

    lyft_button = LyftButton.find(lyft_id=auth_context["lyft_id"])
    dash_button = lyft_button.dash_button if lyft_button else DashButton()

    button = DashButton(
        **{
            field: getattr(new_button, field, None)
            or getattr(dash_button, field, None)
            for field in attr.fields_dict(DashButton).keys()
        }
    )

    lyft_button.dash_button = button

    return button
