import io
import requests
from ..logging import beam_logger as logger

from .client import BeamClient


class HTTPClient(BeamClient):

    def __init__(self, *args, tls=False, headers=None, **kwargs):
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.protocol = 'https' if tls else 'http'
        self._headers = headers
        super().__init__(*args, scheme='beam-http', **kwargs)

    @property
    def headers(self):
        if self._headers is not None:
            return self._headers
        return None

    def get_info(self):
        try:
            return requests.get(f'{self.protocol}://{self.host}/info', headers=self.headers).json()
        except requests.exceptions.JSONDecodeError:
            logger.debug(f"Could not get info from {self.protocol}://{self.host}/info "
                         f"(probably backward compatibility issue)")
            return requests.get(f'{self.protocol}://{self.host}/', headers=self.headers).json()

    def get(self, path, **kwargs):

        response = requests.get(f'{self.protocol}://{self.host}/{path}', headers=self.headers, **kwargs)
        if response.status_code == 200:
            response = self.load_function(io.BytesIO(response.content), **self.lf_kwargs)
        else:
            logger.error(f"Error in get request: (code:{response.status_code})")
            raise Exception(f"Error in get request: {response.content}")

        return response

    def _post(self, path, io_args, io_kwargs, **other_kwargs):

        files = {'args': io_args, 'kwargs': io_kwargs}
        files = {**files, **other_kwargs}

        response = requests.post(f'{self.protocol}://{self.host}/{path}',
                                 files=files, stream=True, headers=self.headers)

        if response.status_code == 200:
            response = self.load_function(io.BytesIO(response.content), **self.lf_kwargs)
        else:
            logger.error(f"Error in get request: (code:{response.status_code})")
            raise Exception(f"Error in post request: {response.content}")

        return response

