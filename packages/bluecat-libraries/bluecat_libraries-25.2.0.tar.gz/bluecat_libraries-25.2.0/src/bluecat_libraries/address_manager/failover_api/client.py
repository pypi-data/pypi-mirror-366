# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Modules for working with BlueCat Address Manager's Failover API."""
from typing import Optional

from bluecat_libraries.http_client import Client as HTTPClient
from bluecat_libraries.address_manager.failover_api.instance import FailoverAPIInstance
from typing import Union


class Client(HTTPClient):
    """
    A client for calling the Failover API of Address Manager.

    The Failover API is a service configuration in Address Manager that can
    enable an externally automated failover when the primary Address Manager
    fails.

    :param url: The base URL of BAM's Failover service. For security reasons,
        the Failover Client always use HTTPS, even if the URL specifies an HTTP scheme.
        If no port is specified within the URL, the client will use port 8444.
    :param cert: Path to an SSL client certificate. The first item being the path to the certificate file
        and the second item is the key.
    :param verify: Whether to verify the server's TLS certificate. If a
        string is passed, it is treated as a path to a CA bundle to
        use. Defaults to ``True``.

    .. versionadded:: 21.5.1
    """

    def __init__(self, url: str, cert: tuple, verify: Union[bool, str] = True):
        super().__init__(target=FailoverAPIInstance(url=url))
        self.session.cert = cert
        self.session.headers = {"Accept": "application/json"}

        self.session.verify = verify

    def get_v1_health(self, timeout: Optional[int] = None) -> dict:
        """
        Return the health status of Address Manager.
        This API can be called on primary, secondary, or standalone Address Manager servers.

        :param timeout: The timeout of this request in milliseconds.
        :return: Returns the health status of Address Manager.

        Example:

            .. code-block:: python

                from bluecat_libraries.address_manager.failover_api import Client

                client_cert = ('client_certificate.crt', 'key.pem')
                server_cert = 'server_certificate.crt'
                with Client(url='https://<bam_address>:8444', cert=client_cert, verify=server_cert) as client:
                    data = client.get_v1_health()
                print(data)

        .. versionadded:: 21.5.1
        """
        params = None
        if timeout:
            params = {"timeout": timeout}
        response = self.http_get(
            url=self._url_for("/bam/v1/health"),
            params=params,
            cert=self.session.cert,
            verify=self.session.verify,
        )
        return response.json()

    def put_v1_promote(self) -> str:
        """
        Promote a secondary Address Manager server in the cluster to primary.

        :return: Returns the health status of Address Manager if successful.

        Example:

            .. code-block:: python

                from bluecat_libraries.address_manager.failover_api import Client

                client_cert = ('client_certificate.crt', 'key.pem')
                server_cert = 'server_certificate.crt'
                with Client(url='https://<bam_address>:8444', cert=client_cert, verify=server_cert) as client:
                    result = client.put_v1_promote()
                print(result)

        .. versionadded:: 21.5.1
        """
        response = self.http_put(
            url=self._url_for("/bam/v1/promote"), cert=self.session.cert, verify=self.session.verify
        )
        return response.json()

    def put_v1_managed_servers_takeover(self) -> list:
        """
        Notify all DNC/DHCP Servers controlled by the old primary Address Manager server
        of the new primary Address Manager server.

        :return: list

        Example:

            .. code-block:: python

                from bluecat_libraries.address_manager.failover_api import Client

                client_cert = ('client_certificate.crt', 'key.pem')
                server_cert = 'server_certificate.crt'
                with Client(url='https://<bam_address>:8444', cert=client_cert, verify=server_cert) as client:
                    data = client.put_v1_managed_servers_takeover()
                print(data)

        .. versionadded:: 21.5.1
        """
        response = self.http_put(
            url=self._url_for("/bam/v1/managed-servers/takeover"),
            cert=self.session.cert,
            verify=self.session.verify,
        )
        return response.json()

    def put_v1_managed_servers_takeover_by_id(self, server_id: int):
        """
        Notify a single DNC/DHCP Server controlled by the old primary Address Manager server
        of the new primary Address Manager server.

        :param server_id: The ID of the DNS/DHCP Server.
        :return: object

        Example:

            .. code-block:: python

                from bluecat_libraries.address_manager.failover_api import Client

                client_cert = ('client_certificate.crt', 'key.pem')
                server_cert = 'server_certificate.crt'
                server_id = 123
                with Client(url='https://<bam_address>:8444', cert=client_cert, verify=server_cert) as client:
                    data = client.put_v1_managed_servers_takeover_by_id(server_id)
                print(data)

        .. versionadded:: 21.5.1
        """
        response = self.http_put(
            url=self._url_for(f"/bam/v1/managed-servers/{server_id}/takeover"),
            cert=self.session.cert,
            verify=self.session.verify,
        )
        return response.json()
