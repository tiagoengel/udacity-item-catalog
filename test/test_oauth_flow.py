import unittest
import unittest.mock as mock
import httplib2
import time
import json

from catalog.auth import oauth, providers
from test import support, mocks

fake_code = 'ZmFrZWZha2VmYWs='


class OauthFlowTest(unittest.TestCase):

    @mock.patch.object(httplib2.Http, "request", mocks.google_oauth_mock())
    def test_google_provider(self):
        flow = oauth.OauthFlow(provider=providers.Google())
        auth = flow.authenticate(fake_code)
        self.assertDictEqual(auth, dict(
            provider=providers.Google.NAME,
            access_token="123456",
            user_data=dict(
                name="john",
                email="john@gmail.com",
                picture="john.png",
                user_id="1234567890"
            )
        ))
        flow.revoke('123456', '1234567890')

    def test_google_provider_raises_error_with_info(self):
        mock_def = {'*': (200, {"error": "there's an error"})}

        request_mocker = support.request_mocker(mock_def)
        mocked_request = mock.Mock(side_effect=request_mocker)

        flow = oauth.OauthFlow(provider=providers.Google())

        @mock.patch.object(httplib2.Http, "request", mocked_request)
        def authenticate():
            return flow.authenticate(fake_code)

        with self.assertRaisesRegex(oauth.OauthError, 'Google: '):
            authenticate()

    @mock.patch.object(httplib2.Http, "request", mocks.facebook_oauth_mock())
    def test_facebook_provider(self):
        flow = oauth.OauthFlow(provider=providers.Facebook())
        auth = flow.authenticate(fake_code)

        self.assertDictEqual(auth, dict(
            provider=providers.Facebook.NAME,
            access_token="123456",
            user_data=dict(
                name="john",
                email="john@gmail.com",
                picture="john.png",
                user_id="1234567890"
            )
        ))

        flow.revoke('123456', '1234567890')

    def test_facebook_provider_raises_error_with_info(self):
        mock_def = {'*': (200, {"error": "there's an error"})}

        request_mocker = support.request_mocker(mock_def)
        mocked_request = mock.Mock(side_effect=request_mocker)

        flow = oauth.OauthFlow(provider=providers.Facebook())

        @mock.patch.object(httplib2.Http, "request", mocked_request)
        def authenticate():
            return flow.authenticate(fake_code)

        with self.assertRaisesRegex(oauth.OauthError, 'Facebook: '):
            authenticate()
