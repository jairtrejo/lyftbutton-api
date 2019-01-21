import os

import attr
import jwt
import structlog

logger = structlog.get_logger(__name__)


@attr.s
class Policy:
    effect = attr.ib(validator=attr.validators.in_(("Allow", "Deny")))

    def asdict(self):
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": self.effect,
                    "Resource": "*",
                }
            ],
        }


@attr.s
class AuthResponse:
    lyft_id = attr.ib(default=None)

    @property
    def principal_id(self):
        if self.lyft_id:
            return "lyft"
        else:
            return "anonymous"

    @property
    def context(self):
        context = {}

        if self.lyft_id:
            context["lyft_id"] = self.lyft_id

        return context

    @property
    def policy(self):
        return Policy(effect="Allow" if self.lyft_id else "Deny")

    def asdict(self):
        return {
            "principalId": self.principal_id,
            "context": self.context,
            "policyDocument": self.policy.asdict(),
        }


def handler(event, context):
    token = event["authorizationToken"].split(" ")[-1]
    claims = {}

    auth_response = AuthResponse()

    if token:
        try:
            claims = jwt.decode(
                token, os.environ.get("TOKEN_SECRET"), algorithms=["HS256"]
            )

            if "exp" not in claims:
                logger.error("Token without expiration")

            else:
                auth_response.lyft_id = claims["lyft_id"]

        except jwt.ExpiredSignatureError:
            logger.info("Expired token")

        except jwt.InvalidTokenError:
            logger.warning("Invalid token", token=token)

    return auth_response.asdict()
