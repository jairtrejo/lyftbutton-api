from lyftbutton.utils.lambdafn import api_handler, Response
from lyftbutton.dashbutton import DashButton


@api_handler
def get_dash_button(auth_context=None):
    if not auth_context:
        return Response(status_code=403)
    else:
        button_id = auth_context['button_id']
        button = DashButton.find(button_id=button_id)
        return button
