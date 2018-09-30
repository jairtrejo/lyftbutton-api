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

        if claims:
            claims.pop('lyft_id')

        print("Reading from dynamo", claims)

        return claims.get('button_id', None)

    def _to_dynamo(self, button_id):
        table = dynamodb.Table('Token')

        claims = {
            'button_id': button_id
        }
        claims['lyft_id'] = self.lyft_account.id

        print("Writing to dynamo", claims)

        table.put_item(Item=claims)

    button_id = property(_from_dynamo, _to_dynamo)

    @property
    def jwt(self):
        TOKEN_SECRET = os.environ.get('TOKEN_SECRET')
        token = jwt.encode(
            {'button_id': self.button_id}, TOKEN_SECRET, algorithm='HS256')
        return token.decode('utf-8')
