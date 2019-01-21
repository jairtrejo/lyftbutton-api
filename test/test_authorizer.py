import os
from datetime import datetime, timedelta

import jwt

from lyftbutton.authorizer import handler


def test_allows_valid_token(environment):
    token = jwt.encode(
        {"lyft_id": "lyft:123", "exp": datetime.utcnow() + timedelta(hours=1)},
        os.environ.get("TOKEN_SECRET"),
        algorithm="HS256",
    ).decode("utf-8")

    response = handler({"authorizationToken": token}, None)

    assert response["principalId"] == "lyft"
    assert response["context"]["lyft_id"] == "lyft:123"
    assert response["policyDocument"]["Statement"][0]["Effect"] == "Allow"


def test_denies_expired_token(environment):
    token = jwt.encode(
        {"lyft_id": "lyft:123", "exp": datetime.utcnow() - timedelta(hours=1)},
        os.environ.get("TOKEN_SECRET"),
        algorithm="HS256",
    ).decode("utf-8")

    response = handler({"authorizationToken": token}, None)

    assert response["policyDocument"]["Statement"][0]["Effect"] == "Deny"


def test_denies_invalid_token(environment):
    token = jwt.encode(
        {
            "weird_claim": "lyft:123",
            "exp": datetime.utcnow() - timedelta(hours=1),
        },
        os.environ.get("TOKEN_SECRET"),
        algorithm="HS256",
    ).decode("utf-8")

    response = handler({"authorizationToken": token}, None)

    assert response["policyDocument"]["Statement"][0]["Effect"] == "Deny"


def test_denies_gibberish(environment):
    token = "gibberish"

    response = handler({"authorizationToken": token}, None)

    assert response["policyDocument"]["Statement"][0]["Effect"] == "Deny"


def test_denies_token_without_expiration(environment):
    token = jwt.encode(
        {"lyft_id": "lyft:123"},
        os.environ.get("TOKEN_SECRET"),
        algorithm="HS256",
    ).decode("utf-8")

    response = handler({"authorizationToken": token}, None)

    assert response["policyDocument"]["Statement"][0]["Effect"] == "Deny"
