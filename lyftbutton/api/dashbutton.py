from lyftbutton.utils.lambdafn import api_handler, Response
from lyftbutton.dashbutton import DashButton, Location


@api_handler
def get_dash_button(auth_context=None):
    if not auth_context:
        return Response(status_code=403)

    serial_number = auth_context["serial_number"]
    button = DashButton.find(serial_number=serial_number)
    return button


@api_handler(model=Location)
def set_dash_button_home(location, auth_context=None):
    if not auth_context:
        return Response(status_code=403)

    serial_number = auth_context["serial_number"]
    button = DashButton.find(serial_number=serial_number)
    button.home = location

    return button


@api_handler(model=Location)
def set_dash_button_default_destination(location, auth_context=None):
    if not auth_context:
        return Response(status_code=403)

    serial_number = auth_context["serial_number"]
    button = DashButton.find(serial_number=serial_number)
    button.destination = location

    return button
