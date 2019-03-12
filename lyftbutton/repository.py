import os
from decimal import Decimal

import attr
import boto3

from lyftbutton.dashbutton import DashButton
from lyftbutton.google import GoogleAccount
from lyftbutton.lyft import LyftAccount

LOCAL_DYNAMO_ENDPOINT = "http://docker.for.mac.localhost:8000/"

if os.getenv("AWS_SAM_LOCAL"):
    dynamodb = boto3.resource("dynamodb", endpoint_url=LOCAL_DYNAMO_ENDPOINT)
    os.environ.setdefault("DYNAMO_TABLE_NAME", "LyftButton")
else:
    dynamodb = boto3.resource("dynamodb")


def _from_dynamo(*, lyft_id=None, serial_number=None):
    table = dynamodb.Table(os.getenv("DYNAMO_TABLE_NAME"))

    if not lyft_id:
        items = table.query(
            IndexName="serial_number",
            KeyConditionExpression="serial_number = :serial_number",
            ExpressionAttributeValues={":serial_number": serial_number},
        ).get("Items")
        if items:
            lyft_id = items[0]["lyft_id"]
        else:
            return None

    row = table.get_item(Key={"lyft_id": lyft_id})
    button_data = row.get("Item", None)

    return button_data


def _to_dynamo(lyft_id, fields):
    table = dynamodb.Table(os.getenv("DYNAMO_TABLE_NAME"))

    clauses = ", ".join(
        "{field} = :{field}".format(field=field) for field in fields.keys()
    )

    table.update_item(
        Key={"lyft_id": lyft_id},
        UpdateExpression="SET %s" % clauses,
        ExpressionAttributeValues={
            ":{field}".format(field=field): value
            for field, value in fields.items()
        },
    )


@attr.s
class LyftButton:
    @classmethod
    def find(cls, lyft_id=None, serial_number=None):
        button_data = _from_dynamo(
            lyft_id=lyft_id, serial_number=serial_number
        )

        if button_data:
            return cls(lyft_id=button_data["lyft_id"])
        else:
            return None

    def _get_lyft_account(self):
        button_data = _from_dynamo(lyft_id=self.lyft_id)
        credentials = button_data["lyft_credentials"]

        lyft_account = LyftAccount.from_credentials(credentials)
        # Refresh credentials
        self._set_lyft_account(lyft_account)

        return lyft_account

    def _set_lyft_account(self, lyft_account):
        _to_dynamo(
            self.lyft_id, {"lyft_credentials": lyft_account.credentials}
        )

    def _get_google_account(self):
        button_data = _from_dynamo(lyft_id=self.lyft_id)
        credentials = button_data.get("google_credentials", None)

        if credentials:
            google_account = GoogleAccount.from_credentials(credentials)
        else:
            google_account = None

        return google_account

    def _set_google_account(self, google_account):
        _to_dynamo(
            self.lyft_id,
            {
                "google_credentials": google_account.credentials
                if google_account
                else None
            },
        )

    def _get_dash_button(self):
        button_data = _from_dynamo(lyft_id=self.lyft_id)
        dash_button = button_data.get("dash_button", None)

        return dash_button and DashButton(
            serial_number=dash_button.get("serial_number", None),
            home=dash_button.get("home", None),
            destination=dash_button.get("destination", None),
        )

    def _set_dash_button(self, dash_button):
        if dash_button is None:
            button_data = None
        else:
            button_data = dash_button.asdict()

            for field in ("home", "destination"):
                if button_data[field]:
                    button_data[field]["lat"] = Decimal(
                        "%.6f" % button_data[field]["lat"]
                    )
                    button_data[field]["lng"] = Decimal(
                        "%.6f" % button_data[field]["lng"]
                    )

        _to_dynamo(self.lyft_id, {"dash_button": button_data})

    lyft_id = attr.ib()
    dash_button = property(_get_dash_button, _set_dash_button)
    lyft_account = property(_get_lyft_account, _set_lyft_account)
    google_account = property(_get_google_account, _set_google_account)
