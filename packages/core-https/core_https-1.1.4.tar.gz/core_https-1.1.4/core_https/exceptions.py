# -*- coding: utf-8 -*-

from typing import Dict


class InternalServerError(Exception):
    """ Base class for exceptions on the project and unhandled errors """

    def __init__(self, status_code: int, details: str, *args):
        super(InternalServerError, self).__init__(*args)
        self.status_code = status_code
        self.details = details

    def get_error_info(self) -> Dict:
        return {
            "type": self.__class__.__name__,
            "details": self.details
        }


class ServiceException(InternalServerError):
    """ Exception caused for handled errors within the service """


class AuthenticationException(ServiceException):
    """ Exception caused for authentication [401] issues """


class AuthorizationException(ServiceException):
    """ Exception caused for authentication [403] issues """


class RateLimitException(ServiceException):
    """
    Exception caused [429] when a client has sent too many requests
    to a server within a given time frame.
    """
