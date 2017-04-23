import json
import httplib2

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import os

from catalog.auth import oauth


class Google():
    """Google oauth provider.

    Oauth provider that uses google oauth2
    to sing in users.
    """

    SECRETS_FILE = os.path.join(os.path.dirname(__file__),
                                'google_client_secrets.json')

    CLIENT_ID = json.loads(
        open(SECRETS_FILE, 'r').read())['web']['client_id']

    NAME = 'google'

    def request_long_term_token(self, short_term_token):
        try:
            oauth_flow = flow_from_clientsecrets(Google.SECRETS_FILE,
                                                 scope='')
            oauth_flow.redirect_uri = 'postmessage'
            return oauth_flow.step2_exchange(short_term_token)
        except FlowExchangeError:
            raise oauth.OauthError(Google.NAME,
                                   'Failed to upgrade the authorization code.')

    def request_user_data(self, credentials):
        # Check that the access token is valid.
        access_token = self.extract_token(credentials)
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
               % access_token)

        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            raise oauth.OauthError(
                Google.NAME,
                json.dumps(result.get('error')))

        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            raise oauth.OauthError(
                Google.NAME,
                "Token's user ID doesn't match given user ID.")

        # Verify that the access token is valid for this app.
        if result['issued_to'] != Google.CLIENT_ID:
            raise oauth.OauthError(
                Google.NAME,
                "Token's user ID doesn't match given user ID.")

        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo?access_token=%s&alt=json"  # noqa
        user_data = json.loads(h.request((userinfo_url % access_token), 'GET')[1])
        user_data["user_id"] = gplus_id
        return user_data

    def extract_token(self, credentials):
        return credentials.access_token

