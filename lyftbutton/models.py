import attr


@attr.s
class LyftAuth:
    code = attr.ib()
    state = attr.ib()


@attr.s
class LyftAccount:
    id = attr.ib()
