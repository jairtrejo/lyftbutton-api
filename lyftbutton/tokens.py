import os

import attr
import jwt

from lyftbutton.utils.dynamo import dynamodb


@attr.s
class Token:
    lyft_account = attr.ib()

    def _from_dynamo(self):
        table = dynamodb.Table('Token')

        row = table.get_item(Key={'lyft_id': self.lyft_account.id})
        claims = row.get('Item', {})

        claims.pop('lyft_id', None)

        return claims

    def _to_dynamo(self, claims):
        table = dynamodb.Table('Token')

        claims['lyft_id'] = self.lyft_account.id

        table.put_item(Item=claims)

    def get_button_id(self):
        if not self._button_id:
            claims = self._from_dynamo()
            self._button_id = claims.get('button_id', None)

        return self._button_id

    def set_button_id(self, button_id):
        claims = {
            'button_id': button_id
        }
        self._to_dynamo(claims)

    button_id = property(_from_dynamo, _to_dynamo)

    @property
    def jwt(self):
        TOKEN_SECRET = os.environ.get('TOKEN_SECRET')
        token = jwt.encode(
            {'button_id': self.button_id}, TOKEN_SECRET, algorithm='HS256')
        return token.decode('utf-8')
