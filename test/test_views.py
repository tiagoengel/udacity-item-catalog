import os
import unittest.mock as mock
import unittest
import time
import httplib2
import json

from flask import session

import catalog.views

from catalog import app, db
from catalog.models import Item
from catalog.auth import providers
from test import support, mocks


class FlaskTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.testing = True
        app.secret_key = 'testing'
        db.session.rollback()
        db.session.query(Item).delete()
        db.session.commit()

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


class ItemsTest(FlaskTest):
    def test_create(self):
        self.do_google_login()
        resp = self.app.post('/items/create',
                             data=dict(title='Create item',
                                       description='Test item',
                                       category='Test'))

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(db.session.query(Item).count(), 1)
        item = db.session.query(Item).first()
        self.assertEqual(item.title, 'Create item')
        self.assertEqual(item.description, 'Test item')
        self.assertEqual(item.category, 'Test')

    def test_cant_create_if_not_logged_in(self):
        resp = self.app.post('/items/create',
                             data=dict(title='Create item',
                                       description='Test item',
                                       category='Test'))

        self.assertEqual(resp.status_code, 401)

    def test_cant_create_with_invalid_args(self):
        self.do_google_login()
        resp = self.app.post('/items/create',
                             data=dict())

        self.assertEqual(resp.status_code, 400)

    def test_delete(self):
        self.do_google_login()
        db.session.add(Item(title='Foo', description='bar', category='FooBar'))
        db.session.add(Item(title='Foo1', description='bar', category='FooBar'))
        item = db.session.query(Item).first()

        resp = self.app.post('/items/%s/delete' % (item.id))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(db.session.query(Item).count(), 1)

    def test_cant_delete_if_not_logged_in(self):
        resp = self.app.post('/items/1/delete')
        self.assertEqual(resp.status_code, 401)

    def test_update(self):
        self.do_google_login()
        db.session.add(Item(title='Foo', description='bar', category='FooBar'))
        item = db.session.query(Item).first()

        resp = self.app.post(('/items/%s/update' % (item.id)),
                             data=dict(title='Create item',
                                       description='Test item',
                                       category='Test'))

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(db.session.query(Item).count(), 1)
        item = db.session.query(Item).first()
        self.assertEqual(item.title, 'Create item')
        self.assertEqual(item.description, 'Test item')
        self.assertEqual(item.category, 'Test')

    def test_cant_update_if_not_logged_in(self):
        resp = self.app.post('/items/1/update')
        self.assertEqual(resp.status_code, 401)



