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

    def __init__(
        self,
        status_code: int = 401,
        details: str = "Unauthorized"
    ) -> None:
        super().__init__(status_code=status_code, details=details)


class AuthorizationException(ServiceException):
    """ Exception caused for authorization [403] issues """

    def __init__(
        self,
        status_code: int = 403,
        details: str = "Forbidden"
    ) -> None:
        super().__init__(status_code=status_code, details=details)


class RateLimitException(ServiceException):
    """
    Exception caused [429] when a client has sent too many requests
    to a server within a given time frame.
    """

    def __init__(
        self,
        status_code: int = 429,
        details: str = "Too Many Requests"
    ) -> None:
        super().__init__(status_code=status_code, details=details)
