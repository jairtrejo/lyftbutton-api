from decimal import Decimal
from functools import lru_cache

import attr

from lyftbutton.utils.dynamo import dynamodb
from lyftbutton.lyft import LyftAccount


@lru_cache(maxsize=None)
def _from_dynamo(serial_number=None, lyft_id=None):
    table = dynamodb.Table('LyftButton')

    if not serial_number:
        items = table.query(
            IndexName='lyft_id',
            KeyConditionExpression='lyft_id = :lyft_id',
            ExpressionAttributeValues={
                ':lyft_id': lyft_id
            }
        ).get('Items')
        if items:
            serial_number = items[0]['serial_number']
        else:
            return None

    row = table.get_item(Key={'serial_number': serial_number})
    button_data = row.get('Item', None)

    return button_data


def _to_dynamo(serial_number, field, value):
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
        credentials = button_data['lyft_credentials']

        lyft_account = LyftAccount.from_credentials(credentials)
        # Refresh credentials
        _to_dynamo(
            self.serial_number, 'lyft_credentials', lyft_account.credentials)

        return lyft_account

    def _set_lyft_account(self, lyft_account):
        _to_dynamo(
            self.serial_number, 'lyft_id', lyft_account.id)
        _to_dynamo(
            self.serial_number, 'lyft_credentials', lyft_account.credentials)

    def _get_location(self, field):
        button_data = _from_dynamo(self.serial_number)
        location_data = button_data.get(field, None)
        if location_data:
            location_data = {
                k: float(v)
                for k, v in location_data.items()
            }
        return Location(**location_data) if location_data else None

    def _set_location(self, field, location):
        location_data = {
            k: Decimal('%.4f' % v)
            for k, v in attr.asdict(location).items()
        }
        _to_dynamo(self.serial_number, field, location_data)

    def get_home(self):
        return self._get_location(field='home')

    def set_home(self, location):
        self._set_location(field='home', location=location)

    def get_destination(self):
        return self._get_location(field='destination')

    def set_destination(self, location):
        self._set_location(field='destination', location=location)

    serial_number = attr.ib()
    lyft_account = property(_get_lyft_account, _set_lyft_account)
    home = property(get_home, set_home)
    destination = property(get_destination, set_destination)

    def asdict(self):
        _from_dynamo.cache_clear()
        d = attr.asdict(self)
        d['home'] = self.home and attr.asdict(self.home)
        d['destination'] = self.destination and attr.asdict(self.destination)
        return d
