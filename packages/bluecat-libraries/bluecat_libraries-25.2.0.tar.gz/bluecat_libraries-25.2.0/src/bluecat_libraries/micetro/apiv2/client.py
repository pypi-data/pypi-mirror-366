# Copyright 2024 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Module for the client to work with Micetro's REST API."""
import base64
import requests

from json import JSONDecodeError
from typing import Any, Callable, Iterable, IO, Optional, Union
from urllib3.util import parse_url

from bluecat_libraries.http_client import (
    Client as HTTPClient,
    ClientError,
    Instance,
    GeneralError,
    UnexpectedResponse,
    version,
)
from bluecat_libraries.micetro.apiv2.constants import ResponseMessage, MediaType
from bluecat_libraries.micetro.apiv2.exceptions import MicetroV2ErrorResponse


__all__ = ["Client"]


class _Instance(Instance):
    """
    Definition of the Micetro REST API service. It is used as a target by a client.

    It holds a URL to the root of the Micetro.
    It holds a URL to the root of the Micetro REST API.

    The path, query, and fragments portions of the input URL will be ignored,
    even if provided.

    .. note:: For internal use *only*.

    :meta private:

    .. versionadded:: 24.3.0
    """

    def parse_url(self):
        """
        Process the service's URL and construct the value of the base URL of
        the service's API.
        """
        self.url = self.url._replace(auth=None, path=None, query=None, fragment=None)
        self.api_url_base = self.url._replace(path="/mmws/api/v2")


class Client(HTTPClient):
    """
     A client for making HTTP calls to Micetro REST API.

     There is a method for each HTTP verb - GET, POST, PUT, PATCH, and DELETE -
     as well as a generic method for a HTTP request: http_get, http_post,
     http_put, http_patch, http_delete, and http_request. The functionality of
     the client relies on the use of these methods.

     The benefits of this client over a direct use of the ``requests`` Python
     library are:

         1.  Available methods for performing authentication.
         2.  The client keeps track of the authentication token and automatically
             sends it with each request.
         3.  The client keeps track of the base API URL, needing only the
             relative path to be specified when making a request.
         4.  The client automatically parses the responses and returns Python
             data structures - dictionaries or strings - based on the response
             content type.
         5.  The client detects error responses and raises a Python exception,
             which holds the fields that the Micetro API replied with, e.g, code.

     Overall, users of the client can write less code and keep track of less data
     when making requests to the Micetro REST API.

     Nonetheless, the client allows for taking advantage of the full
     functionality of the Micetro REST API by exposing all available ``requests``
     parameters in its methods. That way a user can, for example, specify filters
     and fields selection through URL query parameters.

    You need to authenticate to the Micetro REST API via the client method (with a username
     and a password) when making calls. The client will use HTTP header ``Authorization`` as per the
     Micetro documentation.

     .. note:: The client does not specify a value for the `Accept` header by
         default. This results in the `Content-Type` of the response to be
         determined by the defaults of Micetro.

     Example:

     .. code-block:: python

         from bluecat_libraries.micetro.apiv2 import Client, MediaType

         # Retrieve the users. Request the data as per Micetro's default content type.
         with Client(<micetro_url>) as client:
             client.authenticate(<username>, <password>)
             response = client.http_get("/users")
             users = response["result"]["users"]
             for user in users:
                 print(f'{user["ref"]}: {user["name"]}')

         # Retrieve the users. Request that the response is in 'XML' format.
         with Client(<micetro_url>) as client:
             client.authenticate(<username>, <password>)
             response = client.http_get(
                 "/users",
                 headers={"Accept": MediaType.XML},
             )
             print(response)

     .. versionadded:: 24.3.0
    """

    def __init__(self, url: str, *, verify: Any = True) -> None:
        u = parse_url(url)
        if not u.host:
            raise ClientError("The Micetro URL does not contain a host. It is required.")

        super().__init__(_Instance(url))
        self.session.verify = verify
        self.__version = None  # The version of Micetro

    # region Authentication

    @staticmethod
    def generate_token(username, password) -> str:
        """
        Generate a token following the Basic Authentication standard.

        :param username: The username for the Micetro account.
        :param password: The password associated with the username.
        """
        credentials = f"{username}:{password}"
        credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return f"Basic {credentials}"

    def clear_token(self) -> None:
        """Clear token from client and session header"""
        self.token_type = None
        self.token = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

    def authenticate(self, username: str, password: str, refresh_token: bool = False) -> str:
        """
        Logs into Micetro using encoded credentials.

        Creates a base64-encoded token from the provided username and password,
        verifies it with Micetro to ensure the credentials are valid,
        and stores the token for use in subsequent API calls.

        When the client is already authenticated, this function behaves as follows:
            - If ``refresh_token`` is ``False``, it raises a ``ClientError('Client is already authenticated.')``.
            - If ``refresh_token`` is ``True``, it returns a newly generated token.

        :param username: The username for the Micetro account.
        :param password: The password associated with the username.
        :param refresh_token: Retrieve a new token even if logged in.
        :return: A string that contains the authentication token.

        Example:

            .. code:: python

                from bluecat_libraries.micetro.apiv2 import Client

                with Client(<micetro_url>) as client:
                    client.authenticate(<micetro_username>, <micetro_password>)

        .. versionadded:: 24.3.0
        """
        if self.is_authenticated and not refresh_token:
            raise ClientError("Client is already authenticated.")

        self.auth = self.generate_token(username, password)
        return self.auth

    # endregion Authentication

    # region Inherited interfaces

    def _url_for(self, name: str) -> str:
        # NOTE: The `self.api_url_base` does not end with `/`.
        # The value of `name` is expected to start with `/`.
        return self.target.api_url_base.url + name

    def _handle_request_exc(self, exc: Exception) -> None:
        """
        Handle the exception that is raised when the request is attempted.

        :param exc: The exception raised when the HTTP request is made.
        :raises GeneralError: When the request to Micetro fails.

        This method is not intended to be called by users of the class. It is
        present to modify the behaviour inherited from the base class.
        """
        raise GeneralError("The request to Micetro REST API v2 failed.") from exc

    def _handle_error_response(self, response: requests.Response) -> None:
        """
        Handle a response that's considered to be an error (based on the HTTP
        status code). The standard implementation raises an exception.

        :param response: Object representing the HTTP response.

        .. versionchanged:: 24.3.0
        """
        response_content_type = response.headers.get("Content-Type")
        if MediaType.JSON in response.headers["Content-Type"].lower():
            try:
                data = response.json()
            except Exception as exc:
                raise UnexpectedResponse(
                    "The Micetro REST API v2 error response is not valid JSON,"
                    " despite the specified content type.",
                    response,
                ) from exc
            raise MicetroV2ErrorResponse(
                message=data["error"]["message"],
                response=response,
                code=data["error"]["code"],
            )
        raise UnexpectedResponse(
            "The Micetro REST API v2 error response does not have JSON content"
            f" type as expected: {response_content_type}",
            response,
        )

    def _handle_nonerror_response(self, response: requests.Response) -> Union[str, dict]:
        """
        Handle a response that's considered to be a success (non error), based
        on the HTTP status code. Depending on the content type of the response,
        its body is either parsed as JSON and the resulting object returned, or
        returned as verbatim text.

        :param response: Object representing the HTTP response.
        :return: The result of the handled response.
        """
        response_content_type = response.headers.get("Content-Type")
        if response_content_type and MediaType.JSON in response_content_type:
            try:
                # At times, the responses from the PUT, POST, and DELETE methods in Micetro
                # may not include JSON data.
                content = response.json()
            except JSONDecodeError:
                content = response.text
            return content
        return response.text

    def http_request(
        self,
        method: str,
        url: str,
        params: Optional[Union[dict, list[tuple], bytes]] = None,
        data: Optional[Union[dict, list[tuple], bytes, IO]] = None,
        headers: Optional[dict] = None,
        cookies: Optional[dict] = None,
        files: Optional[dict[str, IO]] = None,
        auth: Optional[Union[tuple, Callable]] = None,
        timeout: Optional[Union[float, tuple]] = None,
        allow_redirects: bool = True,
        proxies: Optional[dict] = None,
        hooks: Optional[dict] = None,
        stream: Optional[bool] = None,
        verify: Union[bool, str] = None,
        cert: Optional[Union[str, tuple[str, str]]] = None,
        json: Optional[Any] = None,
        expected_status_codes: Optional[Iterable[int]] = None,
    ) -> Union[dict, str]:
        """
        Perform an HTTP request to the Micetro using the provided
        parameters.

        The call will be made through the instance of ``requests.Session`` that
        the client maintains. The parameters have the same behaviour as their
        namesakes in the ``requests`` library. The only exception is ``url``,
        whose value should be relative to the Micetro URL, e.g.,
        ``"/users"``.

        :param method: HTTP method to be used, e.g., ``GET``, ``POST``,
            ``PUT``, ``PATCH``, ``DELETE``.
        :param url: A URL, relative to the API root to be used for the request,
            e.g., ``/users``. It must start with a forward slash.
        :param params: Query parameters to be passed in the request.
        :param data: Value to send in the body of the request. It can be
            a dictionary, list of tuples, bytes, or file-like object.
        :param headers: HTTP headers to send with the request.
        :param cookies: Cookies to send with the request.
        :param files: File-like objects for multipart encoding upload, e.g.
            ``{"filename": file_like_object}``
        :param auth: Object to handle HTTP Authentication.
        :param timeout: How long to wait to receive data before giving up. If
            given as a tuple, it is used as (connect, read) timeouts.
        :param allow_redirects: Whether to allow redirects. Defaults to
            ``True``.
        :param proxies: Mapping of protocol or protocol and hostname to a URL
            of a proxy to be used.
        :param hooks: Hooks to be called upon events.
        :param stream: Whether to immediately read the response content.
            Defaults to ``False``.
        :param verify: Whether to verify the server's TLS certificate. If a
            string is passed, it is treated as a path to a CA bundle to be
            used. Defaults to ``True``.
        :param cert: Path to a SSL client certificate file (.pem). If the
            certificate has a key, it can be provided as the second item in a
            tuple, with the first item being the path to the certificate file.
        :param json: Object to be sent as JSON in the body of the request.
        :param expected_status_codes: HTTP status codes that are acceptable as
            a status code of the HTTP response. If the received code does not
            match the passed values, an :py:exc:`UnexpectedResponse` is raised.
            If left empty, the status code validation is not performed.
        :return: The data the API responded with. The client will process the
            response based on the stated content type and return either the
            JSON formatted data parsed into a Python object (e.g., a ``dict``)
            or the verbatim body text.

        Example:

        .. code-block:: python

            from bluecat_libraries.micetro.apiv2 import Client

            # Retrieve the users. Request the data as per Micetro's default content type.
            with Client(<micetro_host_url>) as client:
                client.login(<username>, <password>)
                response = client.http_request("GET", "/users")
                users = response["result"]["users"]
                for user in users:
                    print(f'{user["ref"]}: {user["name"]}')
        """
        url = self._url_for(url)
        return super().http_request(
            method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json,
            expected_status_codes=expected_status_codes,
        )

    def http_get(
        self,
        url: str = "",
        params=None,
        expected_status_codes: Optional[Iterable[int]] = None,
        **kwargs,
    ) -> Union[dict, str]:
        """
        Perform an HTTP ``GET`` request based on the provided parameters.
        See method ``http_request`` for details.

        If ``expected_status_codes`` is not specified, it defaults to ``(200, )``.
        ``200`` is the HTTP status code for successful response ``OK``.
        """
        if expected_status_codes is None:
            expected_status_codes = (requests.codes.ok,)
        return self.http_request(
            "GET", url, params, expected_status_codes=expected_status_codes, **kwargs
        )

    def http_post(
        self,
        url: str,
        params=None,
        data=None,
        json: Optional[Any] = None,
        expected_status_codes: Optional[Iterable[int]] = None,
        **kwargs,
    ) -> Union[dict, str]:
        """
        Perform an HTTP ``POST`` request based on the provided parameters.
        See method ``http_request`` for details.
        """
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
        self,
        url: str,
        params=None,
        data=None,
        json: Optional[Any] = None,
        expected_status_codes: Optional[Iterable[int]] = None,
        **kwargs,
    ) -> Union[dict, str]:
        """
        Perform an HTTP ``PUT`` request based on the provided parameters.
        See method ``http_request`` for details.
        """
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
        self,
        url: str,
        params=None,
        data=None,
        json: Optional[Any] = None,
        expected_status_codes: Optional[Iterable[int]] = None,
        **kwargs,
    ) -> Union[dict, str]:
        """
        Perform an HTTP ``PATCH`` request based on the provided parameters.
        See method ``http_request`` for details.
        """
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
        self,
        url: str,
        params=None,
        data=None,
        json: Optional[Any] = None,
        expected_status_codes: Optional[Iterable[int]] = None,
        **kwargs,
    ) -> Union[dict, str]:
        """
        Perform an HTTP ``DELETE`` request based on the provided parameters.
        See method ``http_request`` for details.
        """
        return self.http_request(
            "DELETE",
            url,
            params,
            data,
            json=json,
            expected_status_codes=expected_status_codes,
            **kwargs,
        )

    # endregion Inherited interfaces

    # region Micetro REST v2 API specific interfaces

    @property
    def auth(self) -> Union[str, None]:
        """
        The value that the client is configured to use for header ``Authorization`` when making
        requests to REST API.
        """
        return self.session.headers.get("Authorization")

    @auth.setter
    def auth(self, value: str) -> None:
        """
        Set the value to use for header ``Authorization``. It is used for authenticating the
        requests to the Micetro REST API.

        :param value: Token to be used for Micetro authentication.
        """
        if not value:
            raise ClientError("Empty value for authentication to Micetro REST v2 API.")
        if not value.startswith("Basic"):
            raise ClientError("Micetro REST v2 API only supports Basic authentication.")
        try:
            self.http_get("/addressSpaces", headers={"Authorization": value}, params={"limit": 1})
        except MicetroV2ErrorResponse as exc:
            # These two exceptions explicitly describe the token as not acceptable by Micetro
            # RESTv2. Other exceptions indicating the user does not have required permission
            # will not raise during this authentication, they should be raised in the user's
            # next request and handled by http_request.
            if ResponseMessage.INVALID_USERNAME_OR_PASSWORD == str(
                exc
            ) or ResponseMessage.MISSING_SESSION_ID == str(exc):
                raise exc
        self.token_type = "Basic"
        self.token = value
        self.session.headers.update({"Authorization": value})

    @property
    def micetro_url(self) -> str:
        """
        A URL to the Micetro server the client is created for.

        This is not the verbatim value given during initialization. It contains
        only the scheme, host, and (if specified) port, which will be used by
        the client.
        """
        return self.target.url.url

    @property
    def micetro_version(self) -> version.Version:
        """
        The version of Micetro the client is connected to.

        .. note:: The client does not have to be authenticated to get version.
        """
        if self.__version is None:
            # This API is an alternative to the one `GET /micetro` which requires
            # administrative access to obtain version.
            # The response of this API depends on whether user authenticated or not,
            # but the `centralVersion` is always included. To avoid the inconsistency
            # and ensure authenticated users without any roles do not encounter exceptions
            # while retrieving version, thereby the `Authorization` in header is always
            # overridden, regardless of whether user is authenticated or not.
            response = self.http_get("/command/web_getPreLoginInfo", headers={"Authorization": ""})
            central_version = response["result"]["centralVersion"]
            self.__version = version.parse_version(central_version)
        return self.__version

    # endregion Micetro REST v2 API specific interfaces
