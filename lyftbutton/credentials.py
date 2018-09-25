import attr


@attr.s
class Credentials:
    button_id = attr.ib()

    def get_lyft_credentials(self):
        return '123'

    def set_lyft_credentials(self, credentials):
        pass

    lyft = property(get_lyft_credentials, set_lyft_credentials)
