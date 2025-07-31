# Copyright 2020-2023 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Module for a base HTTP client."""
from http.cookiejar import CookieJar
import requests
from requests import codes, Response
from typing import Any, Callable, IO, Optional, Union

from bluecat_libraries.http_client.exceptions import (
    GeneralError,
    ClientError,
    ErrorResponse,
    UnexpectedResponse,
)
from bluecat_libraries.http_client.instance import Instance

__all__ = ["Client"]


class Client:
    """
    An HTTP client with some utilities to make creating service clients easier.
    The class implements the necessary methods to act as a context manager.

    :param target: A definition of a target service.

    .. versionadded:: 20.6.1

    .. versionchanged:: 23.3.0
        Method ``is_error_response`` has been changed to ``_is_error response`` and
        ``handle_error_response`` has been changed to ``_handle_error_response``.
    """

    def __init__(self, target: Instance):
        self.session = requests.Session()
        self.target = target
        self.token = None
        self.token_type = None

        self._last_response: Optional[Response] = None
        """
        The last response object that was received. It is ``None`` if no request has been made yet
        or if the last request failed and thus there is no ``Response`` object.
        
        .. warning:: This is for *internal* use only!
        
        .. versionadded:: 23.1.0
        """

    def close(self):
        """Release any allocated resources, e.g., an internal session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @property
    def is_authenticated(self) -> bool:
        """Determine whether the authentication necessary to communicate with the target service is set."""
        return bool(self.token)

    def _require_auth(self):
        """
        Raise exception if the client does not have the necessary authentication
        set to communicate with the target service.
        """
        if not self.is_authenticated:
            raise ClientError("Use of this method requires authentication, but none is provided.")

    def _url_for(self, name: str) -> str:
        name = name.lstrip("/")
        return self.target.api_url_base.url + name

    def _is_error_response(self, response: requests.Response) -> bool:
        """
        Determine whether a response is an error response.

        This method exists to allow derived classes to customize the behaviour.

        :param response: Object representing the HTTP response.
        :return: Whether the response conveys an error.

        :meta public:

        .. versionchanged:: 23.3.0
        """
        return not response.ok

    def _handle_request_exc(self, exc: Exception) -> None:
        """
        Handle the exception that is raised when the request is attempted.
        The standard implementation raises a ``GeneralError`` from the passed
        exception.

        :param exc: The exception raised when the HTTP request is made.
        :raises GeneralError: When the request to the target service fails.

        .. note::
            It is expected that this method raises an exception.

        .. note::
            This method is not intended to be called by users of the class.
            Derived classes may overwrite this method and customize the
            behaviour, e.g., change the exception type and/or the message.

        :meta public:

        .. versionadded:: 23.1.0
        """
        raise GeneralError("Error communicating with target service.") from exc

    def _handle_error_response(self, response: requests.Response):
        """
        Handle a response that's considered to be an error (based on the HTTP
        status code). The standard implementation raises an exception. Derived
        classes may overwrite it to provide custom handling.

        :param response: Object representing the HTTP response.

        :meta public:

        .. versionchanged:: 23.3.0
        """
        raise ErrorResponse(
            "Response with HTTP status code {}".format(response.status_code), response
        )

    def _handle_nonerror_response(self, response: requests.Response) -> Any:
        """
        Handle a response that's considered to be a success (non error) by
        ``is_error_response``. The standard implementation simply returns the
        response object.

        :param response: Object representing the HTTP response.
        :return: The result of the handled response.

        .. note::
            This method is not intended to be called by users of the class.
            Derived classes may overwrite this method and customize the
            behaviour, e.g., parse the response body into a typed structure.

        :meta public:

        .. versionadded:: 23.1.0
        """
        return response

    def http_request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        data: Optional[Union[dict, list[tuple], bytes, IO]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[CookieJar] = None,
        files: Optional[dict] = None,
        auth: Optional[Union[tuple, Callable]] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: Optional[bool] = True,
        proxies: Optional[dict] = None,
        hooks: Optional[dict] = None,
        stream: Optional[bool] = None,
        verify: Optional[Union[bool, str]] = None,
        cert: Optional[Union[str, tuple]] = None,
        json: Optional[object] = None,
        expected_status_codes: Optional[int] = None,
    ) -> Response:
        """
        Perform an HTTP request based on the provided parameters. It is done
        as part of the internally maintained session, i.e. using the set
        authorization. The majority of the method's parameters correspond to
        their namesakes in :py:meth:`requests.Session.request`. However, this
        class additionally processes the response. It uses
        :py:meth:`is_error_response` and :py:meth:`handle_error_response` to
        detect and handle error responses. That approach allows derived classes
        to customize the behaviour. Additionally, it checks the HTTP status
        code against provided `expected_status_codes` and raises an exception.

        :param method: HTTP method to be used.
        :param url: URL to be used for the request.
        :param params: Query parameters to be passed in the request.
        :param data: Value to be sent in the body of the request.
        :param headers: HTTP Headers to be sent with the request.
        :param cookies: Cookies to be sent with the request.
        :param files: File-like objects for multipart encoding upload.
        :param auth: Object to handle HTTP Authentication.
        :param timeout: How long to wait to receive data before giving up. If
            given as a tuple, it is used as (connect, read) timeouts.
        :param allow_redirects: Whether to allow redirects. Defaults to ``True``.
        :param proxies: Mapping of protocol or protocol and hostname to a URL
            of a proxy to be used.
        :param hooks: Hooks to be called upon events.
        :param stream: Whether to immediately read the response content.
            Defaults to ``False``.
        :param verify: Whether to verify the server's TLS certificate. If a
            string is passed, it is treated as a path to a CA bundle to be
            used. Defaults to ``True``.
        :param cert: Path to a SSL client certificate file (.pem). If the
            certificate has a key, it can be provides as the second item in a
            tuple, with the first item being the path to the certificate file.
        :param json: Object to be sent as JSON in the body of the request.
        :param expected_status_codes: HTTP status codes that are acceptable as
            a status code of the HTTP response. If the received code does not
            match the passed values, an :py:exc:`UnexpectedResponse` is raised.
            If left empty, the status code validation is not performed.
        :return: Object representing the HTTP response received to the performed
            request.

        .. versionchanged:: 23.1.0
            If parameter ``verify`` is ``None``, the value of ``verify`` from
            the underlying session object is used explicitly.

            .. warning::
                This is not backward-compatible behaviour.
                However, it is a necessary workaround for issue
                `#3829 <https://github.com/psf/requests/issues/3829>`_ of the
                ``requests`` library that affects instances of the client used
                in BlueCat Gateway workflows or Adaptive Applications.
        """
        verify = self.session.verify if verify is None else verify
        try:
            response = self.session.request(
                method,
                url,
                params,
                data,
                headers,
                cookies,
                files,
                auth,
                timeout,
                allow_redirects,
                proxies,
                hooks,
                stream,
                verify=verify,
                cert=cert,
                json=json,
            )
            self._last_response = response
        except Exception as exc:
            self._last_response = None
            self._handle_request_exc(exc)

        if self._is_error_response(response):
            self._handle_error_response(response)

        if expected_status_codes and response.status_code not in expected_status_codes:
            raise UnexpectedResponse("Response with unexpected HTTP status code.", response)

        return self._handle_nonerror_response(response)

    def http_get(self, url, params=None, expected_status_codes=None, **kwargs) -> Response:
        """
        Perform an HTTP GET request based on the provided parameters. See
        `http_request` for details.

        If `expected_status_codes` is not specified, it defaults to `(200, )`.
        200 is the HTTP status code for successful response `OK`.
        """
        if expected_status_codes is None:
            expected_status_codes = (codes.ok,)
        return self.http_request(
            "GET", url, params, expected_status_codes=expected_status_codes, **kwargs
        )

    def http_post(
        self, url, params=None, data=None, json=None, expected_status_codes=None, **kwargs
    ) -> Response:
        """Perform an HTTP POST request based on the provided parameters. See `http_request` for details."""
        return self.http_request(
            "POST",
            url,
            params,
            data,
            json=json,
            expected_status_codes=expected_status_codes,
            **kwargs,
        )

    def http_put(
        self, url, params=None, data=None, json=None, expected_status_codes=None, **kwargs
    ) -> Response:
        """Perform an HTTP PUT request based on the provided parameters. See `http_request` for details."""
        return self.http_request(
            "PUT",
            url,
            params,
            data,
            json=json,
            expected_status_codes=expected_status_codes,
            **kwargs,
        )

    def http_patch(
        self, url, params=None, data=None, json=None, expected_status_codes=None, **kwargs
    ) -> Response:
        """Perform an HTTP PATCH request based on the provided parameters. See `http_request` for details."""
        return self.http_request(
            "PATCH",
            url,
            params,
            data,
            json=json,
            expected_status_codes=expected_status_codes,
            **kwargs,
        )

    def http_delete(
        self, url, params=None, data=None, json=None, expected_status_codes=None, **kwargs
    ) -> Response:
        """Perform an HTTP DELETE request based on the provided parameters. See `http_request` for details."""
        return self.http_request(
            "DELETE",
            url,
            params,
            data,
            json=json,
            expected_status_codes=expected_status_codes,
            **kwargs,
        )
