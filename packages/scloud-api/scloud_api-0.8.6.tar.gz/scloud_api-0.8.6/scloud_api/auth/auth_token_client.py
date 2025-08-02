import os

import requests
import hashlib
from cachetools import TTLCache

from .credentials import Credentials
from .auth_token_response import AuthTokenResponse
from .exceptions import AuthException

cache = TTLCache(maxsize=int(os.environ.get('SCLOUD_API_AUTH_CACHE_SIZE', 10)), ttl=int(os.environ.get('SCLOUD_API_AUTH_CACHE_TTL', 3000)))

class AuthTokenClient:
    path = "/api/token"
    url = False

    def __init__(self, cred):
        self.cred = Credentials(cred)

    def _request(self, url, data, headers):
        resp = requests.post(url+self.path, json=data, headers=headers, timeout=30)
        data = resp.json()
        if resp.status_code != 200:
            raise AuthException(data['Message'])
        else:
            return data


    def _get_url(self, team_name):
        url = f"https://api.sellercloud.com/api/server-by-team/?team={team_name}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if 'Success' in data and data['Success'] == False:
            raise AuthException(data['Message'])
        else:
            return data['RestApiEndpoint']

    def get_auth(self) -> AuthTokenResponse:
        if not self.url:
            self.url = self._get_url(self.cred.team_id)

        cache_key = self._get_cache_key()

        try:
            access_token = cache[cache_key]
        except KeyError:
            access_token = self._request(self.url, self.data, self.headers)
            cache[cache_key] = access_token
        vals = {
            "url": self.url,
            "access_token": access_token['access_token'],
        }
        return AuthTokenResponse(**vals)

    def _get_cache_key(self, token_flavor=''):
        return 'access_token_' + hashlib.md5(
            (token_flavor + (self.cred.user_name or '__grantless__')).encode('utf-8')
        ).hexdigest()

    @property
    def data(self):
        return {
            "Username": self.cred.user_name,
            "Password": self.cred.password
        }

    @property
    def headers(self):
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }