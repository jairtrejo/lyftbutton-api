import json
from functools import wraps

import attr


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
        return {
            'statusCode': self.status_code,
            **{'body': self.body, 'headers': self.headers}
        }


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
            parameters = event.get('queryStringParameters', {}) or {}
            auth_context = context.get('authorizer', None)

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
                return {
                    'statusCode': 400
                }

            if not isinstance(response, Response):
                response = Response(
                    status_code=200,
                    body=json.dumps(attr.asdict(response)))

            return response.asdict()

        return api_method

    if len(args):
        return to_handler(args[0])
    else:
        return to_handler
