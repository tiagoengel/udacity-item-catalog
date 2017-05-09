import os
import unittest.mock as mock
import unittest
import time
import httplib2
import json

from flask import session

import catalog.views

from catalog import app
from catalog.auth import providers
from test import support


class FlaskTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.testing = True
        app.secret_key = 'testing'


class ViewsTest(FlaskTest):
    def test_connect_with_google(self):
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
            return self.app.post('/oauth-connect/Google',
                                 data=json.dumps(dict(token='123456')),
                                 content_type='application/json')

        resp = authenticate()
        self.assertEqual(resp.status_code, 204)

    def test_connect_with_facebook(self):
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
            return self.app.post('/oauth-connect/Facebook',
                                 data=json.dumps(dict(token='123456')),
                                 content_type='application/json')

        resp = authenticate()
        self.assertEqual(resp.status_code, 204)

    def test_connect_with_invalid_provider(self):
        resp = self.app.post('/oauth-connect/Amazon',
                             data=json.dumps(dict(token='123456')),
                             content_type='application/json')

        self.assertEqual(resp.status_code, 401)

