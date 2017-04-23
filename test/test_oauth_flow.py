import unittest
import unittest.mock as mock
import httplib2
import time
import json

from catalog.auth import oauth, providers

jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"  # noqa

# {
#   "sub": "1234567890",
#   "name": "John Doe",
#   "admin": true
# }

resp = {"access_token": "123456",
        "refresh_token": "new_token",
        "user_id": "1234567890",  # same as 'sub' on the JWT token
        "expires_in": time.time(),
        "issued_to": providers.Google.CLIENT_ID,
        "id_token": jwt_token}

auth_response = httplib2.Response({
    "status": 200,
    "body": json.dumps(resp),
})


class OauthFlowTest(unittest.TestCase):
    def test_google_oauth_flow(self):
        fake_code = 'ZmFrZWZha2VmYWs='
        flow = oauth.OauthFlow(provider=providers.Google())

        def mock_response(url, *args, **kwargs):
            if url.startswith('https://www.googleapis.com/oauth2/v1/userinfo'):
                return (auth_response, json.dumps({
                    "name": "john",
                    "email": "john@gmail.com",
                    "picture": "john.png",
                }))
            else:
                return (auth_response, json.dumps(resp))

        mocked_request = mock.Mock(side_effect=mock_response)

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