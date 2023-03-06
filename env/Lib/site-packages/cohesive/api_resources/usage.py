from dataclasses import dataclass

import requests
import json
import cohesive 
from cohesive.error import IdempotencyError, APIConnectionError, APIError
from cohesive.params import BaseParams


@dataclass
class UsageParams(BaseParams):
    workspace_id: int
    instance_id: int
    units: int
    timestamp: int


class Usage:
    @classmethod
    def report(cls, params: UsageParams):
        if not params.idempotency_key:
            raise IdempotencyError
        try:
            response = requests.post(f'{cohesive.api_base}/report-usage', data=json.dumps(params.__dict__), headers={'Authorization': f'Bearer {cohesive.api_key}'})
            response.raise_for_status()
        except ConnectionError as e:
            raise APIConnectionError(message=str(e), http_status=None, http_body=None, http_headers=None)
        except requests.HTTPError as e:
            raise APIError(message=str(e), http_status=e.response.status_code, http_body=e.response.text, http_headers=e.response.headers)
        except requests.Timeout as _:
            raise APIError(message='Timed out', http_status=None, http_body=None, http_headers=None)
        except requests.TooManyRedirects as _:
            raise APIError(message='Too many redirects', http_status=None, http_body=None, http_headers=None)