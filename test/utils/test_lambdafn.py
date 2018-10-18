import json

import attr
import pytest

from lyftbutton.utils.lambdafn import Response, api_handler


@pytest.fixture
def event():
    return {"queryStringParameters": None}


@pytest.fixture
def context():
    return {}


@pytest.fixture
def model_instance():
    def _model_instance(**kwargs):
        class S:
            def asdict(self):
                return attr.asdict(self)

        C = attr.make_class("MyModel", list(kwargs.keys()), bases=(S,))
        return C(**kwargs)

    return _model_instance


class TestApiHandler:
    def test_returns_response_from_handler(self, event, context):
        @api_handler
        def handler():
            return Response(status_code=404, headers={"Location": "elsewhere"})

        response = handler(event, context)

        assert response["statusCode"] == 404
        assert response["headers"]["Location"] == "elsewhere"

    def test_serializes_return_value_if_not_response(
        self, event, context, model_instance
    ):
        @api_handler
        def handler():
            return model_instance(some="dict")

        response = handler(event, context)

        assert response["statusCode"] == 200
        assert response["body"] == '{"some": "dict"}'

    def test_passes_query_parameters_as_keyword_arguments(
        self, event, context, model_instance
    ):
        @api_handler
        def handler(param=None):
            return model_instance(param=param)

        event["queryStringParameters"] = {"param": "value"}

        response = handler(event, context)

        assert response["body"] == '{"param": "value"}'

    def test_returns_400_for_invalid_parameters(self, event, context):
        @api_handler
        def handler():
            return Response(status_code=200)

        event["queryStringParameters"] = {"param": "value"}

        response = handler(event, context)

        assert response["statusCode"] == 400

    def test_passes_auth_context_if_available(self, event, context):
        @api_handler
        def handler(auth_context):
            return Response(status_code=200, body=auth_context["principalId"])

        event["requestContext"] = {"authorizer": {"principalId": "some-id"}}

        response = handler(event, context)

        assert response["body"] == "some-id"

    def test_doesnt_pass_auth_context_if_anonymous(self, event, context):
        @api_handler
        def handler(auth_context=None):
            return Response(status_code=200, body=auth_context)

        event["requestContext"] = {"authorizer": {"principalId": "anonymous"}}

        response = handler(event, context)

        assert response.get("body") is None

    def test_builds_model_if_requested(self, event, context):
        MyModel = attr.make_class("MyModel", ["foo"])

        @api_handler(model=MyModel)
        def handler(instance):
            return Response(status_code=200, body=instance.foo)

        event["body"] = json.dumps({"foo": "bar"})

        response = handler(event, context)

        assert response["body"] == "bar"

    def test_returns_400_for_invalid_model(self, event, context):
        MyModel = attr.make_class("MyModel", ["foo"])

        @api_handler(model=MyModel)
        def handler(instance):
            return Response(status_code=200, body=instance.foo)

        event["body"] = json.dumps({"baz": "bar"})

        response = handler(event, context)

        assert response["statusCode"] == 400

    def test_returns_404_when_response_is_none(self, event, context):
        @api_handler
        def handler():
            return None

        response = handler(event, context)

        assert response["statusCode"] == 404
