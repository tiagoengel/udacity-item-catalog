class OauthFlow():
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


class OauthError(Exception):
    pass

