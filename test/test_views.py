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
from test import support, mocks


class FlaskTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.testing = True
        app.secret_key = 'testing'

    def do_google_login(self):
        @mock.patch.object(httplib2.Http, "request", mocks.google_oauth_mock())
        def authenticate():
            return self.app.post('/oauth-connect/Google',
                                 data=json.dumps(dict(token='123456')),
                                 content_type='application/json')

        return authenticate()

    def do_facebook_login(self):
        @mock.patch.object(httplib2.Http, "request", mocks.facebook_oauth_mock())
        def authenticate():
            return self.app.post('/oauth-connect/Facebook',
                                 data=json.dumps(dict(token='123456')),
                                 content_type='application/json')

        return authenticate()


class LoginLogoutTest(FlaskTest):
    def test_connect_with_google(self):
        resp = self.do_google_login()
        self.assertEqual(resp.status_code, 204)

    def test_connect_with_facebook(self):
        resp = self.do_facebook_login()
        self.assertEqual(resp.status_code, 204)

    def test_connect_with_invalid_provider(self):
        resp = self.app.post('/oauth-connect/Amazon',
                             data=json.dumps(dict(token='123456')),
                             content_type='application/json')

        self.assertEqual(resp.status_code, 401)

    def test_logout(self):
        self.do_google_login()

        @mock.patch.object(httplib2.Http, "request", mocks.google_oauth_mock())
        def logout():
            return self.app.post('/logout')

        self.assertEqual(logout().status_code, 302)
