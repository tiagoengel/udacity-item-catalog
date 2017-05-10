import time
import unittest.mock as mock

from catalog.auth import providers
from test import support


def google_oauth_mock():
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"  # noqa

    mock_def = {'https://www.googleapis.com/oauth2/v1/userinfo':
                (200, {"name": "john",
                        "email": "john@gmail.com",
                        "picture": "john.png"}),
                'https://accounts.google.com/o/oauth2/revoke':
                (200, {}),
                '*':
                (200, {"access_token": "123456",
                        "refresh_token": "new_token",
                        # same as 'sub' on the JWT token
                        "user_id": "1234567890",
                        "expires_in": time.time(),
                        "issued_to": providers.Google.CLIENT_ID,
                        "id_token": jwt_token})}

    request_mocker = support.request_mocker(mock_def)
    return mock.Mock(side_effect=request_mocker)


def facebook_oauth_mock():
    mock_def = {'https://graph.facebook.com/v2.8/me':
                (200, {"id": "1234567890",
                        "name": "john",
                        "email": "john@gmail.com",
                        "picture": "john.png"}),
                'https://graph.facebook.com/oauth/access_token':
                (200, {"access_token": "123456",
                        "expires_in": time.time()}),
                'https://graph.facebook.com/v2.8/me/picture':
                (200, {'data': {'url': 'john.png'}}),
                'https://graph.facebook.com/1234567890/permissions':
                (200, {})}

    request_mocker = support.request_mocker(mock_def)
    return mock.Mock(side_effect=request_mocker)