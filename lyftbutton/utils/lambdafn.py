import json
import os
from functools import wraps

import attr
import jwt
import structlog

import lyftbutton.logconfig as logconfig

logger = structlog.get_logger(__name__)


@attr.s
class Response:
    """
    An HTTP response
    """

    status_code = attr.ib()
    body = attr.ib(default=None)
    headers = attr.ib(factory=dict)

    def set_cookie(self, name, value):
        self.headers["Set-Cookie"] = name + "=" + value
        return self

    def asdict(self):
        response = {"statusCode": self.status_code}
        if self.body is not None:
            response["body"] = self.body
        if len(self.headers) != 0:
            response["headers"] = self.headers

        return response


def authorizer(event, context):
    """
    An API Gateway authorizer

    Args:
        event (dict) The authorization event
        context (dict) Lambda execution context

    Returns:
        response (dict) An auth_context dictionary
    """
    TOKEN_SECRET = os.environ.get("TOKEN_SECRET")
    auth_header = event["headers"].get("Authorization")

    if auth_header:
        claims = jwt.decode(
            auth_header.split(" ")[1], TOKEN_SECRET, algorithm="HS256"
        )
        claims["principalId"] = "button"
    else:
        claims = {"principalId": "anonymous"}

    return claims


def api_handler(*args, model=None):
    """
        A decorator for API call handlers

        Args:
            model (class): An attr class to build an instance from JSON body.
    """

    def to_handler(f):
        """
        A decorator for API call handlers

        Args:
            f (function): A function that returns a :class:`Response`, or a
            JSON serializable value.
        """

        @wraps(f)
        def api_method(event, context):
            logconfig.configure()
            log = logger.new(
                request_id=context.aws_request_id,
                method=event["httpMethod"],
                resource=event["resource"],
            )

            # Query parameters
            query_parameters = event.get("queryStringParameters", {}) or {}

            # Authorization
            if os.getenv("AWS_SAM_LOCAL"):
                auth_context = authorizer(event, context)
            else:
                auth_context = event.get("requestContext", {}).get(
                    "authorizer", None
                )

            if auth_context and auth_context["principalId"] != "anonymous":
                log = log.bind(user=auth_context["lyft_id"])

            # Model
            if model:
                try:
                    instance = model(**json.loads(event["body"]))
                except TypeError as e:
                    logger.error(
                        "Invalid model",
                        model=model,
                        body=event["body"],
                        exc_info=e,
                    )

                    return Response(
                        status_code=400,
                        body=json.dumps(
                            {
                                "message": "Invalid {model}".format(
                                    model=model.__name__
                                )
                            }
                        ),
                    ).asdict()

            try:
                args = [instance] if model else []
                kwargs = {
                    **query_parameters,
                    **(
                        {"auth_context": auth_context}
                        if auth_context
                        and auth_context["principalId"] != "anonymous"
                        else {}
                    ),
                }

                response = f(*args, **kwargs)

            except TypeError as e:
                logger.error(
                    "Validation error", args=args, kwargs=kwargs, exc_info=e
                )

                response = Response(
                    status_code=400,
                    body=json.dumps({"message": "Invalid request parameters"}),
                )

            except Exception:
                logger.error("Unexpected error")
                return Response(status_code=500)

            if not response:
                response = Response(status_code=404)

            elif not isinstance(response, Response):
                body = json.dumps(response.asdict())
                response = Response(status_code=200, body=body)

            if 200 <= response.status_code < 300:
                logger.info(
                    "Success", response=response, status=response.status_code
                )
            else:
                logger.info(
                    "Failure", response=response, status=response.status_code
                )

            return response.asdict()

        return api_method

    if len(args):
        # The @api_handler(Model) use case
        return to_handler(args[0])

    else:
        # The plain @api_handler use case
        return to_handler
