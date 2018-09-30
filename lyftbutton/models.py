import attr


@attr.s
class LyftAuth:
    state = attr.ib()
    code = attr.ib()


@attr.s
class LyftAccount:
    id = attr.ib()
    first_name = attr.ib()
    last_name = attr.ib()
    has_taken_a_ride = attr.ib()
