# -*- coding: utf-8 -*-

try:
    from enum import StrEnum

except ImportError:
    from core_mixins.compatibility import StrEnum


class StatusInfo(StrEnum):
    """
    StatusInfo is a literal representation of the response depending on
    the status_code received...

      * success: is for HTTP statuses 1XX, 2XX and 3XX.
      * error: is for HTTP statuses from 400 to 499.
      * fail: is for HTTP statuses from 500 to 599.
    """

    SUCCESS = "success"
    ERROR = "error"
    FAILURE = "failure"
