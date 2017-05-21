class OauthFlow():
    """Create or revoke oauth tokens using a `provider`.

    A valid provider must implement four required functions.
        - request_long_term_token
        - request_user_data
        - extract_token
        - revoke

    Returns
        A dictionary containing the provider name, the long term access token
        and the user data. (name, email, picture and id)
    """
    def __init__(self, provider):
        self.provider = provider

    def authenticate(self, token):
        try:
            credentials = self.provider.request_long_term_token(token)
            user_data = self.provider.request_user_data(credentials)
            access_token = self.provider.extract_token(credentials)
        except Exception as e:
            raise OauthError('%s: %s' % (self.provider.NAME, str(e))) from e

        return dict(provider=self.provider.NAME,
                    access_token=access_token,
                    user_data=user_data)

    """Revokes a long term token.

    This will effectively logout the user.
    """
    def revoke(self, token, user_id):
        try:
            self.provider.revoke(token, user_id)
        except Exception as e:
            raise OauthError('%s: %s' % (self.provider.NAME, str(e))) from e


class OauthError(Exception):
    pass

