from functools import lru_cache

import attr

from lyftbutton.utils.dynamo import dynamodb
from lyftbutton.lyft import LyftAccount


@lru_cache(maxsize=None)
def _from_dynamo(serial_number=None, lyft_id=None):
    table = dynamodb.Table('LyftButton')

    if not serial_number:
        items = dynamodb.query(
            TableName='LyftButton',
            IndexName='lyft_id',
            ExpressionAttributeValues={
                ':lyft_id': {
                    'S': lyft_id
                }
            },
            KeyConditionExpression='lyft_id = :lyft_id'
        ).get('Items')
        serial_number = items[0]['serial_number']

    row = table.get_item(Key={'serial_number': serial_number})
    button_data = row.get('Item', None)

    if button_data:
        button_data.pop('serial_number')

    return button_data


def to_dynamo(serial_number, field, value):
    table = dynamodb.Table('LyftButton')

    table.update_item(
        Key={
            'serial_number': serial_number
        },
        UpdateExpression='SET %s = :value' % field,
        ExpressionAttributeValues={
            ':value': value
        }
    )


@attr.s
class Location:
    lat = attr.ib()
    lng = attr.ib()


@attr.s
class DashButton:
    serial_number = attr.ib()

    @classmethod
    def find(cls, button_id=None, lyft_id=None):
        button_data = _from_dynamo(
            serial_number=button_id, lyft_id=lyft_id)

        if button_data:
            return cls(serial_number=button_data['serial_number'])
        else:
            return None

    def _get_lyft_account(self):
        button_data = _from_dynamo(self.serial_number)
        lyft_account = LyftAccount.from_credentials(
            button_data['lyft_credentials'])
        # Refresh credentials
        to_dynamo(
            self.serial_number, 'lyft_credentials', lyft_account.credentials)

        return lyft_account

    def _set_lyft_account(self, lyft_account):
        to_dynamo(
            self.serial_number, 'lyft_credentials', lyft_account.credentials)

    lyft_account = property(_get_lyft_account, _set_lyft_account)
