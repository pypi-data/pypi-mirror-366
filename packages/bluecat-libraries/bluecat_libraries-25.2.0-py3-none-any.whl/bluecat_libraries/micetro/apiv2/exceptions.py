# Copyright 2024 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Module with exceptions that may occur while working with Micetro."""
from requests import Response

from bluecat_libraries.http_client import ErrorResponse

__all__ = ["MicetroV2ErrorResponse"]


class MicetroV2ErrorResponse(ErrorResponse):
    """
    This exception is raised when an error response is received from a target.
    The HTTP response is available via the `response` instance member.
    """

    def __init__(self, message: str, response: Response, code: str, *args, **kwargs):
        super().__init__(message, response, *args, **kwargs)
        self.code = code

    def __repr__(self):
        return f"{self.__class__.__name__}({self.message!r} [{self.code}])"
