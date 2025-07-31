# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Module with exceptions that may occur while working with BlueCat Address Manager."""
from requests import Response
from bluecat_libraries.http_client import ErrorResponse


__all__ = ["BAMV2ErrorResponse"]


class BAMV2ErrorResponse(ErrorResponse):
    """
     This exception is raised when an error response is received from a target.
     The HTTP response is available via the `response` instance member.

    :param message: Description of API error code.
    :param response: The HTTP response resulting from a request.
    :param status: HTTP status code of error (400-599).
    :param reason: Reason phrase of status code.
    :param code: API error code.

    Example:

    .. code-block:: python

        from bluecat_libraries.address_manager.apiv2 import Client, BAMV2ErrorResponse

        with Client(<bam_host_url>) as client:
            try:
                # This will fail because the authentication is missing.
                response = client.http_get("/configurations")
            except BAMV2ErrorResponse as exc:
                print(exc.message)
                print(exc.status)
                print(exc.reason)
                print(exc.code)

        >>> The request authorization credentials are either missing or invalid
        >>> 401
        >>> Unauthorized
        >>> InvalidAuthorizationCredentials
    """

    def __init__(
        self,
        message: str,
        response: Response,
        status: int,
        reason: str,
        code: str,
    ):
        super().__init__(message, response)
        self.status = status
        self.reason = reason
        self.code = code

    def __repr__(self):
        return f"{self.__class__.__name__}({self.message!r} [{self.code}, {self.reason}, {self.status}])"
