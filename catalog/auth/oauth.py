class OauthFlow():
    def __init__(self, provider):
        self.provider = provider

    def authenticate(self, short_term_token):
        credentials = self.provider.request_long_term_token(short_term_token)
        user_data = self.provider.request_user_data(credentials)
        access_token = self.provider.extract_token(credentials)

        return dict(provider=self.provider.NAME,
                    access_token=access_token,
                    user_data=user_data)


class OauthError(Exception):
    def __init__(self, provider, message):
        super(OauthError, self).__init__('%s: %s' % (provider, message))

