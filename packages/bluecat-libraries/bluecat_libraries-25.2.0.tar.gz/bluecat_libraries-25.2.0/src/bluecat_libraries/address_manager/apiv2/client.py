# Copyright 2023-2025 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Module for the client to work with BlueCat Address Manager's API v2."""
from __future__ import annotations
from bluecat_libraries.address_manager.apiv2.constants import MediaType
from bluecat_libraries.address_manager.apiv2.exceptions import BAMV2ErrorResponse
from bluecat_libraries.http_client import (
    Client as HTTPClient,
    ClientError,
    GeneralError,
    Instance,
    UnexpectedResponse,
    version,
)
import copy
import requests
from urllib3.util import parse_url
from typing import Any, Callable, Iterable, IO, Optional, Union


__all__ = ["Client"]


class _Instance(Instance):
    """
    Definition of the BAM REST v2 API service. It is used as a target by a client.

    It holds a URL to the root of the BlueCat Address Manager.
    It holds a URL to the root of the BlueCat Address Manager REST API v2.

    The path, query, and fragments portions of the input URL will be ignored,
    even if provided.

    .. note:: For internal use *only*.

    :meta private:

    .. versionadded:: 23.1.0
    """

    def parse_url(self):
        """
        Process the service's URL and construct the value of the base URL of
        the service's API.
        """
        self.url = self.url._replace(auth=None, path=None, query=None, fragment=None)
        self.api_url_base = self.url._replace(path="/api/v2")


class Client(HTTPClient):
    """
    A client for making HTTP calls to BAM REST v2 API.

    There is a method for each HTTP verb - GET, POST, PUT, PATCH, and DELETE -
    as well as a generic method for a HTTP request: http_get, http_post,
    http_put, http_patch, http_delete, and http_request. The functionality of
    the client relies on the use of these methods.

    The benefits of this client over a direct use of the ``requests`` Python
    library are:

        1.  Available methods for performing login and logout, as well as
            determining the version of the BlueCat Address Manager.
        2.  The client keeps track of the authentication token and automatically
            sends it with each request.
        3.  The client keeps track of the base API URL, needing only the
            relative path to be specified when making a request.
        4.  The client automatically parses the responses and returns Python
            data structures - dictionaries or strings - based on the response
            content type.
        5.  The client detects error responses and raises a Python exception,
            which holds the fields that the BAM API replied with, e.g, code.

    Overall, users of the client can write less code and keep track of less data
    when making requests to the BAM REST v2 API.

    Nonetheless, the client allows for taking advantage of the full
    functionality of the BAM REST v2 API by exposing all available ``requests``
    parameters in its methods. That way a user can, for example, specify filters
    and fields selection through URL query parameters.

    You need to authenticate to the BAM REST v2 API when making calls. The
    client will use HTTP header ``Authorization`` as per the BAM documentation.
    You have to either perform a login via the client method (with a username
    and a password) or set the ``auth`` property to the full value for the
    header, including the authorization scheme.

    .. note:: The client does not specify a value for the `Accept` header by
        default. This results in the `Content-Type` of the response to be
        determined by the defaults of BAM.

    Example:

    .. code-block:: python

        from bluecat_libraries.address_manager.apiv2 import Client, MediaType
        import csv

        # Retrieve the configurations. Request the data as per BAM's default content type.
        with Client(<bam_host_url>) as client:
            client.login(<username>, <password>)
            response = client.http_get("/configurations")
            configurations = response["data"]
            for configuration in configurations:
                print(f'{configuration["id"]}: {configuration["name"]}')
            client.logout()

        # Retrieve the configurations. Request that the response is in 'JSON' format.
        # The result should contain only fields 'id' and 'name'.
        with Client(<bam_host_url>) as client:
            client.login(<username>, <password>)
            response = client.http_get(
                "/configurations",
                params={"fields": "id,name"},
                headers={"Accept": MediaType.JSON},
            )
            configurations = response["data"]
            for configuration in configurations:
                print(f'{configuration["id"]}: {configuration["name"]}')
            client.logout()

        # Retrieve configurations. Request that the response is in 'CSV' format.
        # The result should contain only the first 10, ordered alphabetically by name.
        with Client(<bam_host_url>) as client:
            client.login(<username>, <password>)
            configurations_csv = client.http_get(
                "/configurations",
                params={"orderBy": "asc(name)", "limit": "10"},
                headers={"Accept": MediaType.CSV},
            )
            configurations = list(csv.reader(configurations_csv.splitlines()))
            for configuration in configurations:
                # NOTE: The 'id' is the first value in a row, the 'name' is the third one.
                print(f"{configuration[0]}: {configuration[2]}")
            client.logout()

    .. versionadded:: 23.1.0
    """

    def __init__(self, url: str, *, verify: Any = True) -> None:
        u = parse_url(url)
        # if not u.scheme:
        #     raise ClientError("The BAM URL does not contain a scheme. It is required.")
        if not u.host:
            raise ClientError("The BAM URL does not contain a host. It is required.")

        super().__init__(_Instance(url))
        self.session.verify = verify
        self.__session_data = None
        self.__version = None  # The version of BAM.

    # region Inherited interfaces

    def _url_for(self, name: str) -> str:
        # NOTE: The `self.api_url_base` does not end with `/`.
        # The value of `name` is expected to start with `/`.
        return self.target.api_url_base.url + name

    def _handle_request_exc(self, exc: Exception) -> None:
        """
        Handle the exception that is raised when the request is attempted.

        :param exc: The exception raised when the HTTP request is made.
        :raises GeneralError: When the request to BlueCat Address Manager fails.

        This method is not intended to be called by users of the class. It is
        present to modify the behaviour inherited from the base class.
        """
        raise GeneralError("The request to BlueCat Address Manager REST API v2 failed.") from exc

    def _handle_error_response(self, response: requests.Response) -> None:
        """
        Handle a response that's considered to be an error (based on the HTTP
        status code). The standard implementation raises an exception.

        :param response: Object representing the HTTP response.

        .. versionchanged:: 23.3.0
        """
        response_content_type = response.headers.get("Content-Type")
        if response_content_type == "application/json":
            try:
                content = response.json()
            except Exception as exc:
                raise UnexpectedResponse(
                    "The BAM REST API v2 error response is not valid JSON,"
                    " despite the specified content type.",
                    response,
                ) from exc
            raise BAMV2ErrorResponse(
                message=content["message"],
                response=response,
                status=content["status"],
                code=content["code"],
                reason=content["reason"],
            )
        raise UnexpectedResponse(
            "The BAM REST API v2 error response does not have JSON content"
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
        content = (
            response.json()
            if response_content_type and "json" in response_content_type
            else response.text
        )
        return content

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
        Perform an HTTP request to the Address Manager using the provided
        parameters.

        The call will be made through the instance of ``requests.Session`` that
        the client maintains. The parameters have the same behaviour as their
        namesakes in the ``requests`` library. The only exception is ``url``,
        whose value should be relative to the Address Manager URL, e.g.,
        ``"/configurations"``.

        :param method: HTTP method to be used, e.g., ``GET``, ``POST``,
            ``PUT``, ``PATCH``, ``DELETE``.
        :param url: A URL, relative to the API root to be used for the request,
            e.g., ``/configurations``. It must start with a forward slash.
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
            certificate has a key, it can be provides as the second item in a
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

            from bluecat_libraries.address_manager.apiv2 import Client

            # Retrieve the configurations. Request the data as per BAM's default content type.
            with Client(<bam_host_url>) as client:
                client.login(<username>, <password>)
                response = client.http_request("GET", "/configurations")
                configurations = response["data"]
                for configuration in configurations:
                    print(f'{configuration["id"]}: {configuration["name"]}')
                client.logout()
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

        .. note:: From BAM v9.5.0, we can use the GET request to filter data
            without ``url`` in the prefix.
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
    # region BAM REST v2 API specific interfaces

    @property
    def auth(self) -> str | None:
        """
        The value that the client is configured to use for header ``Authorization`` when making
        requests to BAM REST v2 API.
        """
        return self.session.headers.get("Authorization", None)

    @auth.setter
    def auth(self, value: str) -> None:
        """
        Set the value to use for header ``Authorization``. It is used for authenticating the
        requests to the BAM REST v2 API.

        :param value: Token to be used for BAM authentication.
        """
        # Added in the initial version: 23.1.0
        if not value:
            raise ClientError(
                "Empty value for authentication to BAM REST v2 API."
                " If you need to clear the authentication, use the deleter."
            )

        self.__session_data = self.http_get("/sessions/current", headers={"Authorization": value})
        pos = value.find(" ")
        if pos > -1:
            self.token_type = value[:pos]
            self.token = value[pos + 1 :]
        else:
            self.token_type = None
            self.token = value
        self.session.headers.update({"Authorization": value})

    @auth.deleter
    def auth(self) -> None:
        """Clear the value to use for header ``Authorization``."""
        # Added in the initial version: 23.1.0
        self.token_type = None
        self.token = None
        self.session.headers.pop("Authorization", None)

    @property
    def bam_url(self) -> str:
        """
        A URL to the Address Manager the client is created for.

        This is not the verbatim value given during initialization. It contains
        only the scheme, host, and (if specified) port, which will be used by
        the client.
        """
        # Added in the initial version: 23.1.0
        return self.target.url.url

    @property
    def bam_version(self) -> version.Version:
        """
        The version of the BlueCat Address Manager the client is connected to.

        .. note:: The client has to be authenticated before the version can be
            determined.

        :return: Version of BlueCat Address Manager.
        """
        # Added in the initial version: 23.1.0
        if not self.__version:
            params = {"filter": "type:'SystemSettings'"}
            response = self.http_get("/settings", params=params)
            try:
                v = response["data"][0].get("version").split("-")[0]
            except Exception as exc:
                raise UnexpectedResponse(
                    "The BAM response does not contain a version value formatted as expected.",
                    self._last_response,
                ) from exc
            self.__version = version.parse_version(v)
        return self.__version

    @property
    def is_authenticated(self) -> bool:
        """
        Whether the authentication necessary to communicate with the BlueCat
        Address Manager REST v2 API is set.
        """
        # Added in the initial version: 23.1.0
        return bool(self.session.headers.get("Authorization", False))

    @property
    def username(self) -> str | None:
        """
        Username of the user that is currently authenticated with BlueCat Address Manager.

        .. note:: The client has to be authenticated before the username can be determined.

        :return: Username string, or None if not authenticated.
        """
        # Added in the initial version: 25.2.0
        if not self.__session_data:
            return None
        return self.__session_data["user"]["name"]

    def login(self, username: str, password: str) -> dict:
        """
        Log user into BAM and store authentication token for later use by subsequent calls.

        :param username: BAM username.
        :param password: BAM password.

        :return: The session information returned by BAM API v2 basic authentication token.
        """
        # Added in the initial version: 23.1.0
        data = {"username": username, "password": password}
        self.__session_data = self.http_post("/sessions", json=data)
        self.auth = "Basic " + self.__session_data["basicAuthenticationCredentials"]
        return copy.deepcopy(self.__session_data)

    def logout(self) -> dict:
        """
        Log user out from BAM and clear any stored authentication token.

        :return: The logged-out session information is returned by BAM API v2.
        """
        # Added in the initial version: 23.1.0
        sessions_id = self.__session_data["id"]
        data = {"state": "LOGGED_OUT"}
        headers = {"Content-Type": MediaType.MERGE_PATCH_JSON}
        res = self.http_patch(f"/sessions/{sessions_id}", json=data, headers=headers)
        self.__session_data = None
        del self.auth
        return res

    # endregion BAM REST v2 API specific actions
