import requests
from typing import Optional, Dict


class OPNClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str, ssl_verify: bool = True):
        self._api_key = api_key
        self._api_secret = api_secret
        self._base_url = base_url.rstrip('/')
        if not self._base_url.endswith('/api'):
            self._base_url += '/api'
        self._ssl_verify = ssl_verify

        # Cache the different modules
        self._diagnostics = None

    @property
    def diagnostics(self):
        if self._diagnostics is None:
            from .modules.diagnostics import Diagnostics
            self._diagnostics = Diagnostics(self)


        return self._diagnostics

    def _get_response(self, uri_path: str, params: Optional[Dict]=None, method: str='GET'):
        url = f'{self._base_url}/{uri_path}?'

        if method == 'GET':
            return requests.get(
                url,
                params=params,
                verify=self._ssl_verify,
                auth=(self._api_key, self._api_secret),
            )
        elif method == 'POST':
            return requests.post(
                url,
                json=params,
                verify=self._ssl_verify,
                auth=(self._api_key, self._api_secret)
            )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
