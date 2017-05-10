import json
import httplib2
import os

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from catalog.auth import oauth


class Google():
    """Google oauth provider.

    Oauth provider that uses google oauth2
    to sign in users.
    """

    SECRETS_FILE = os.path.join(os.path.dirname(__file__),
                                'google_client_secrets.json')

    CLIENT_ID = json.loads(open(SECRETS_FILE, 'r').read())['web']['client_id']

    NAME = 'Google'

    def request_long_term_token(self, short_term_token):
        try:
            oauth_flow = flow_from_clientsecrets(Google.SECRETS_FILE,
                                                 scope='')
            oauth_flow.redirect_uri = 'postmessage'
            return oauth_flow.step2_exchange(short_term_token)
        except FlowExchangeError:
            raise oauth.OauthError('Failed to upgrade the authorization code.')

    def request_user_data(self, credentials):
        # Check that the access token is valid.
        access_token = self.extract_token(credentials)
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
               % access_token)

        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            raise oauth.OauthError(result.get('error'))

        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            raise oauth.OauthError("Token's user ID doesn't match given user ID.")

        # Verify that the access token is valid for this app.
        if result['issued_to'] != Google.CLIENT_ID:
            raise oauth.OauthError("Token's user ID doesn't match given user ID.")

        info_url = "https://www.googleapis.com/oauth2/v1/userinfo?access_token=%s&alt=json"  # noqa
        user_data = json.loads(h.request((info_url % access_token), 'GET')[1])
        user_data["user_id"] = gplus_id
        return user_data

    def extract_token(self, credentials):
        return credentials.access_token

    def revoke(self, token, user_id):
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % token
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
        status = result['status']
        if status != 200:
            raise oauth.OauthError(('Unable to revoke token. [%s]' % status))


class Facebook():
    """Facebook oauth2 provider.

    Authenticates users using facebook oauth2 provider.
    """

    SECRETS_FILE = os.path.join(os.path.dirname(__file__),
                                'fb_client_secrets.json')

    SECRETS = json.loads(open(SECRETS_FILE, 'r').read())['web']
    APP_ID = SECRETS['app_id']
    APP_SECRET = SECRETS['app_secret']

    NAME = 'Facebook'

    def request_long_term_token(self, short_term_token):
        url = ('https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'  # noqa
               % (Facebook.APP_ID, Facebook.APP_SECRET, short_term_token))
        h = httplib2.Http()
        credentials = json.loads(h.request(url, 'GET')[1])
        if credentials.get('error'):
            raise oauth.OauthError(credentials['error'])

        return credentials

    def request_user_data(self, credentials):
        token = self.extract_token(credentials)
        user_info_url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email'  # noqa
        h = httplib2.Http()
        result = h.request((user_info_url % token), 'GET')[1]
        user_data = json.loads(result)

        picture_url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200'  # noqa
        h = httplib2.Http()
        result = h.request((picture_url % token), 'GET')[1]
        picture = json.loads(result)

        user_data['user_id'] = user_data['id']
        del user_data['id']
        user_data['picture'] = picture['data']['url']
        return user_data

    def extract_token(self, credentials):
        return credentials["access_token"]

    def revoke(self, token, user_id):
        url = ('https://graph.facebook.com/%s/permissions?access_token=%s'
               % (user_id, token))
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[0]
        status = result['status']
        if status != 200:
            raise oauth.OauthError(('Unable to revoke token. [%s]' % status))


