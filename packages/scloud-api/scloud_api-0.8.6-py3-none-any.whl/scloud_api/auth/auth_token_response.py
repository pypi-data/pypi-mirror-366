class AuthTokenResponse:
    def __init__(self, **kwargs):
        self.url = kwargs.get('url')
        self.access_token = kwargs.get('access_token')