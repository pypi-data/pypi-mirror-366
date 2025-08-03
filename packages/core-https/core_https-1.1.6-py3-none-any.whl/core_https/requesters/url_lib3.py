# -*- coding: utf-8 -*-

import logging

try:
    from http import HTTPMethod

except ImportError:
    from core_https.utils import HTTPMethod

from urllib3 import BaseHTTPResponse
from urllib3 import PoolManager
from urllib3 import Retry

from .base import Requester


class Urllib3Requester(Requester):
    _http = PoolManager()

    def __init__(self, log_level: int = logging.WARNING):
        super(Urllib3Requester, self).__init__()
        logging.getLogger("urllib3").setLevel(log_level)

    @classmethod
    def make_request(
            cls, method: HTTPMethod, url: str, headers=None, fields=None,
            timeout: float = 10, retries: Retry = False,
            **kwargs) -> BaseHTTPResponse:

        return cls._http.request(
            method=str(method), url=url, headers=headers,
            fields=fields, timeout=timeout,
            retries=retries, **kwargs)
