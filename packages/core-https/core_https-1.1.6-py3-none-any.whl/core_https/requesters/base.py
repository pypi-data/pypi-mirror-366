# -*- coding: utf-8 -*-

from abc import abstractmethod

try:
    from http import HTTPMethod

except ImportError:
    from core_https.utils import HTTPMethod

from urllib3 import Retry, BaseHTTPResponse


class Requester:
    """ Base class for all type of HTTP requesters """

    @classmethod
    @abstractmethod
    def make_request(
            cls, method: HTTPMethod, url: str, headers=None, fields=None,
            timeout: float = 10, retries: Retry = False,
            **kwargs) -> BaseHTTPResponse:

        """ Makes the request and returns the response """
