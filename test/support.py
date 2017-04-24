"""
Support/utilities for tests classes
"""

import httplib2
import json


def request_mocker(mock_def):
    """Mock http requests for tests.

    This function will return a new function to be used alongside
    with `unittest.mock` to mock httplib2 requests.

    # Examples

        mock_def = {"http://google.com":
                       (200, {'name': 'john'
                              'age': 18}),
                    "http://facebook.com:
                       (200, {'name': 'joana'
                              'age': 19}),
                    "*": (200, "")}

        mocked_request = mock.Mock(side_effect=request_mocker(mock_def))
    """

    def inner(url, *args, **kargs):
        without_qstring = url.split('?')[0]
        response = mock_def.get(without_qstring)
        if not response:
            response = mock_def.get("*")

        http_response = httplib2.Response({
            "status": response[0],
            "body": json.dumps(response[1]),
        })

        return (http_response, json.dumps(response[1]))

    return inner

