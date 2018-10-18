import attr


def _to_location(value):
    if type(value) is dict:
        return Location(**value)
    else:
        return value


@attr.s
class Location:
    """
    A geographical location
    """

    lat = attr.ib(converter=float)
    lng = attr.ib(converter=float)


@attr.s
class DashButton:
    """
    An Amazon Dash button
    """

    serial_number = attr.ib(default=None)
    home = attr.ib(default=None, converter=_to_location)
    destination = attr.ib(default=None, converter=_to_location)

    def asdict(self):
        return attr.asdict(self)
