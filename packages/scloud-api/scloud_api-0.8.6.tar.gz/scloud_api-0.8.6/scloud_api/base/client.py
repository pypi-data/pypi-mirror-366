from requests import request
import json
from scloud_api.auth import AuthTokenClient
from .ApiResponse import ApiResponse
from ..auth.exceptions import AuthException


class Client:
    def __init__(self, cred=None):
        self.auth = AuthTokenClient(cred)

    def _request(self, path: str, method: str, data: dict = None) -> ApiResponse:
        try:
            self._auth = self.auth.get_auth()
        except AuthException as e:
            return ApiResponse(401,{}, e.message)

        endpoint = f"{self._auth.url}{path}"
        error = ""
        status_code = 0
        result = {}

        try:
            res = request(
                method=method,
                url=endpoint,
                headers=self.headers,
                data=(
                    json.dumps(data)
                    if data and method in ("POST", "PUT", "PATCH")
                    else None
                ),
                params=(
                    data
                    if data and method in ("GET")
                    else None
                ))
            status_code = res.status_code
            result = res.json()
        except AuthException as e:
            error = e.message
            status_code = 401
        return ApiResponse(status_code, result, error)

    @property
    def headers(self):
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self._auth.access_token}",
        }