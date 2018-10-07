import json
import os
from functools import wraps

import attr
import jwt


@attr.s
class Response:
    """
    An HTTP response
    """
    status_code = attr.ib()
    body = attr.ib(default=None)
    headers = attr.ib(factory=dict)

    def set_cookie(self, name, value):
        self.headers['Set-Cookie'] = name + '=' + value
        return self

    def asdict(self):
        response = {
            'statusCode': self.status_code,
        }
        if self.body is not None:
            response['body'] = self.body
        if len(self.headers) != 0:
            response['headers'] = self.headers

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
    TOKEN_SECRET = os.environ.get('TOKEN_SECRET')
    auth_header = event['headers'].get('Authorization')

    if auth_header:
        claims = jwt.decode(
            auth_header.split(' ')[1], TOKEN_SECRET, algorithm='HS256')
        claims['principalId'] = 'button'
    else:
        claims = {'principalId': 'anonymous'}

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
            print("========== DEBUG ===========")
            print(event.get('headers'))
            print(event.get('queryStringParameters'))
            parameters = event.get('queryStringParameters', {}) or {}
            if os.getenv('AWS_SAM_LOCAL'):
                auth_context = authorizer(event, context)
            else:
                auth_context = event.get(
                    'requestContext', {}
                ).get('authorizer', None)

            print('Auth context: ', auth_context)

            if auth_context and auth_context['principalId'] != 'anonymous':
                parameters['auth_context'] = auth_context

            try:
                if model:
                    instance = model(**json.loads(event['body']))
                    response = f(instance, **parameters)
                else:
                    response = f(**parameters)
            except TypeError as e:
                print(e)
                response = Response(
                    status_code=400, body=json.dumps({'message': str(e)}))

            if not isinstance(response, Response):
                response = Response(
                    status_code=200,
                    body=json.dumps(attr.asdict(response)))

            print(response)
            print("============================")

            return response.asdict()

        return api_method

    if len(args):
        return to_handler(args[0])
    else:
        return to_handler
