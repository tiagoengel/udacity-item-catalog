import unittest
import unittest.mock as mock
import httplib2
import time
import json

from catalog.auth import oauth, providers
from test import support

fake_code = 'ZmFrZWZha2VmYWs='


class OauthFlowTest(unittest.TestCase):
    def test_google_provider(self):
        flow = oauth.OauthFlow(provider=providers.Google())
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"  # noqa

        mock_def = {'https://www.googleapis.com/oauth2/v1/userinfo':
                    (200, {"name": "john",
                           "email": "john@gmail.com",
                           "picture": "john.png"}),
                    '*':
                    (200, {"access_token": "123456",
                           "refresh_token": "new_token",
                           # same as 'sub' on the JWT token
                           "user_id": "1234567890",
                           "expires_in": time.time(),
                           "issued_to": providers.Google.CLIENT_ID,
                           "id_token": jwt_token})}

        request_mocker = support.request_mocker(mock_def)
        mocked_request = mock.Mock(side_effect=request_mocker)

        @mock.patch.object(httplib2.Http, "request", mocked_request)
        def authenticate():
            return flow.authenticate(fake_code)

        self.assertDictEqual(authenticate(), dict(
            provider=providers.Google.NAME,
            access_token="123456",
            user_data=dict(
                name="john",
                email="john@gmail.com",
                picture="john.png",
                user_id="1234567890"
            )
        ))

    def test_google_provider_raises_error_with_info(self):
        mock_def = {'*': (200, {"error": "there's an error"})}

        request_mocker = support.request_mocker(mock_def)
        mocked_request = mock.Mock(side_effect=request_mocker)

        flow = oauth.OauthFlow(provider=providers.Google())

        @mock.patch.object(httplib2.Http, "request", mocked_request)
        def authenticate():
            return flow.authenticate(fake_code)

        with self.assertRaisesRegex(oauth.OauthError, 'google: '):
            authenticate()

    def test_facebook_provider(self):
        flow = oauth.OauthFlow(provider=providers.Facebook())

        mock_def = {'https://graph.facebook.com/v2.8/me':
                    (200, {"id": "1234567890",
                           "name": "john",
                           "email": "john@gmail.com",
                           "picture": "john.png"}),
                    'https://graph.facebook.com/oauth/access_token':
                    (200, {"access_token": "123456",
                           "expires_in": time.time()}),
                    'https://graph.facebook.com/v2.8/me/picture':
                    (200, {'data': {'url': 'john.png'}})}

        request_mocker = support.request_mocker(mock_def)
        mocked_request = mock.Mock(side_effect=request_mocker)

        @mock.patch.object(httplib2.Http, "request", mocked_request)
        def authenticate():
            return flow.authenticate(fake_code)

        self.assertDictEqual(authenticate(), dict(
            provider=providers.Facebook.NAME,
            access_token="123456",
            user_data=dict(
                name="john",
                email="john@gmail.com",
                picture="john.png",
                user_id="1234567890"
            )
        ))

    def test_facebook_provider_raises_error_with_info(self):
        mock_def = {'*': (200, {"error": "there's an error"})}

        request_mocker = support.request_mocker(mock_def)
        mocked_request = mock.Mock(side_effect=request_mocker)

        flow = oauth.OauthFlow(provider=providers.Facebook())

        @mock.patch.object(httplib2.Http, "request", mocked_request)
        def authenticate():
            return flow.authenticate(fake_code)

        with self.assertRaisesRegex(oauth.OauthError, 'facebook: '):
            authenticate()
