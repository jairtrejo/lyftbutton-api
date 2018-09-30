from time import time

import attr
from lyft_rides.session import OAuth2Credential

from lyftbutton.utils.dynamo import dynamodb


@attr.s
class Credentials:
    button_id = attr.ib()

    def _to_dynamo(self, table_name, credential_data):
        table = dynamodb.Table(table_name)

        credential_data['serial_number'] = self.button_id

        table.put_item(Item=credential_data)

    def _from_dynamo(self, table_name):
        table = dynamodb.Table(table_name)

        row = table.get_item(Key={'serial_number': self.button_id})
        credential_data = row.get('Item', None)
        if credential_data:
            credential_data.pop('serial_number')

        return credential_data

    def get_lyft_credentials(self):
        credential_data = self._from_dynamo('LyftCredential')

        if credential_data:
            credential_data['expires_in_seconds'] -= int(time())
            credential = OAuth2Credential(**credential_data)
        else:
            credential = None

        return credential

    def set_lyft_credentials(self, credentials):
        credential_data = {
            'client_id': credentials.client_id,
            'access_token': credentials.access_token,
            'expires_in_seconds': credentials.expires_in_seconds,
            'scopes': list(credentials.scopes),
            'grant_type': credentials.grant_type,
            'client_secret': credentials.client_secret,
            'refresh_token': credentials.refresh_token,
        }

        self._to_dynamo('LyftCredential', credential_data)

    lyft = property(get_lyft_credentials, set_lyft_credentials)
