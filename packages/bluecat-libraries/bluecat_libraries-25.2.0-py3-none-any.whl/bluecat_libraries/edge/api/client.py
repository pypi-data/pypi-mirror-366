# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""
Module for the client to work with BlueCat Edge's API.
"""
# pylint: disable=too-many-lines
from typing import IO, Optional
from requests import Response, codes
import urllib
from bluecat_libraries.edge.api.instance import EdgeInstance
from bluecat_libraries.edge.api.exceptions import EdgeErrorResponse
from bluecat_libraries.http_client import Client, ClientError, UnexpectedResponse

__all__ = [
    "EdgeClient",
]


class EdgeClient(Client):
    """`Client` uses the `requests` library to communicate with the REST endpoints of DNS Edge."""

    def __init__(self, url):
        super().__init__(EdgeInstance(url))

    def _handle_error_response(self, response: Response):
        """
        Handle a response that's considered to be an error. If the response
        matches an Edge error, an `EdgeErrorResponse` is raised. Otherwise,
        the handling is delegated to the base class' implementation.

        .. versionchanged:: 23.3.0
        """
        if response.headers["Content-Type"].lower() == "application/json":
            try:
                data = response.json()
                error_message = data["brief"]
                error_code = data["code"]
            except Exception as exc:
                raise UnexpectedResponse(
                    "DNS Edge API returned an error that cannot be processed.", response
                ) from exc
            raise EdgeErrorResponse(error_message, response, error_code)
        super()._handle_error_response(response)

    def clear_token(self):
        """Clear token from client and session header"""
        self.token = None
        self.token_type = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

    # region Authentication
    def authenticate(self, client_id: str, client_secret: str, refresh_token: bool = False):
        """
        Log in to the DNS Edge CI using the access key set to retrieve a token and bearer type to populate the
        authorization header.

        :param client_id: Edge client ID.
        :param client_secret: Edge secret access key.
        :param refresh_token: Retrieve a new token even if logged in.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)

        .. versionadded:: 20.6.1
        """
        if self.is_authenticated and not refresh_token:
            raise ClientError("Client is already authenticated.")

        payload = {
            "grantType": "ClientCredentials",
            "clientCredentials": {"clientId": client_id, "clientSecret": client_secret},
        }

        response = self.http_post(
            self._url_for("/v1/api/authentication/token"),
            json=payload,
            expected_status_codes=(codes.ok,),
        )

        data = response.json()
        self.token = data["accessToken"]
        self.token_type = data["tokenType"]
        self.session.headers["Authorization"] = self.token_type + " " + self.token

    def get_v1_api_authentication_token_describe(self):
        """
        Return information about the user whose credentials were used to obtain
        the authorization token.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    current_user = client.get_v1_api_authentication_token_describe()

                print(current_user)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/authentication/token/describe"))
        return response.json()

    # endregion Authentication

    # region DNS Query Stats
    def get_v1_api_customer_dnsquerystats_count(
        self, start: int, downsample: int, end: Optional[int] = None
    ) -> list[dict]:
        """
        Return the total count of logged DNS queries per policy action type in a Customer Instance for any time
        interval within the last 24 hours.

        :param start: The start of the time range, in milliseconds since the Unix Epoch.
        :param downsample: The sample period in the returned dataset, in minutes.
        :param end: The end of the time range, in milliseconds since the Unix Epoch.
        :return: DNS query count results including columns: time, totalQueries, totalAllowed, totalMonitored,
         totalRedirected, totalNonMatched

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                start = 0         # Start of time range
                downsample = 10   # Sample period of returned dataset

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    stats = client.get_v1_api_customer_dnsquerystats_count(start=start, downsample=downsample)

                for stat in stats:
                    print(stat)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_get(
            self._url_for("/v1/api/customer/dnsQueryStats/count"),
            params={"start": start, "end": end, "downsample": downsample},
        )
        return response.json()

    def get_v1_api_customer_dnsquerystats_topdomains(
        self, start: int, count: int, end: Optional[int] = None
    ) -> list[dict]:
        """
        Return the specified number of domains most frequently queried per Customer Instance for any time interval
        within the last 24 hours.

        :param start: The start of the time range, in milliseconds since the Unix Epoch.
        :param count: The number of domains to return.
        :param end: The end of the time range, in milliseconds since the Unix Epoch.
        :return: The most frequently queried domains info: domainName, hitcount

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                start = 0         # Start of time range
                count = 10        # Number of results to return

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_customer_dnsquerystats_topdomains(start=start, count=count)

                for domain in result:
                    print(domain)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_get(
            self._url_for("/v1/api/customer/dnsQueryStats/topDomains"),
            params={"start": start, "end": end, "count": count},
        )
        return response.json()

    def get_v1_api_customer_dnsquerystats_uniqueip(
        self, start: int, end: Optional[int] = None
    ) -> dict:
        """
        Return the total number of unique client IPs that issued DNS queries in a Customer Instance for any time
        interval within the last 24 hours.

        :param start: The start of the time range, in milliseconds since the Unix Epoch.
        :param end: The end of the time range, in milliseconds since the Unix Epoch. Defaults to `None`.
        :return: Total number of unique client IPs that issued DNS queries in a Customer Instance with key "count".

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                start = 0         # Start of time range

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    stats = client.get_v1_api_customer_dnsquerystats_uniqueip(start=start)

                print(stats["count"])

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_get(
            self._url_for("/v1/api/customer/dnsQueryStats/uniqueIp"),
            params={"start": start, "end": end},
        )
        return response.json()

    # endregion

    # region Service Point Fleet Management
    def get_v1_api_servicepoints(self) -> list[dict]:
        """
        Return information about all currently registered service points.

        :return: Currently registered service points information including: id, name, siteId, lastSync, connectionState,
            connectionStateLastChanged, ipAddresses, loopbackIps, version, updateInitiatedTimestamp, updateStatus

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_servicepoints()

                for sp in result:
                    print(sp)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/servicePoints"))
        return response.json()

    # endregion

    # region audit logs
    def get_v1_api_audit_logs(
        self,
        offset: Optional[str] = None,
        limit: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        user_name: Optional[str] = None,
    ) -> list:
        """
        Return the audit log records of API requests and responses.

        :param offset: The number of records to skip, from the beginning of the log.
        :param limit: The maximum number of records to retrieve.
        :param start_time: The start time of the period to return logs for, in ISO_8601 format.
        :param end_time: The end time of the period to return logs for, in ISO_8601 format.
        :param user_name: To filter log records for a particular user, specify a user name.
        :return: Audit log records of API requests and responses.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_audit_logs()

                for log in result:
                    print(log)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_get(
            self._url_for("/v1/api/audit/logs"),
            params={
                "offset": offset,
                "limit": limit,
                "startTime": start_time,
                "endTime": end_time,
                "username": user_name,
            },
        )
        return response.json()

    # endregion

    # region Site Administration
    def get_v3_api_sites(
        self,
        name: Optional[str] = None,
        name_contains: Optional[str] = None,
        fields: Optional[str] = None,
        desired_result_count: Optional[int] = None,
        namespace_id: Optional[str] = None,
        overrides_forwarders: Optional[bool] = None,
    ) -> list[dict]:
        """
        Return information about all the sites.

        :param name: Filter by the exact name of a site
        :param name_contains:  Filter sites by part of a site name. The name and name_contains parameters
            are mutually exclusive and shouldn't be used at the same time.
        :param fields: Fields to include in the response.
            Example: ?fields=id,name will return a response that contains only the sites' IDs and names.
        :param desired_result_count: The number of sites to include in the response.
        :param namespace_id: Filter sites by a specific namespace ID.
        :param overrides_forwarders: Determine whether to include sites that have overriding forwarders
            for the specified namespace. Default is false. This parameter is only effective when
            used with the namespaceId parameter.
        :return: Sites information including: id, name, location, settings, registeredServicePointCount,
            version, updateInitiatedTimestamp, updateStatus, blockedServicePointIds

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v3_api_sites()

                for sp in result:
                    print(sp)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        params = {
            "name": name,
            "nameContains": name_contains,
            "fields": fields,
            "desiredResultCount": desired_result_count,
            "namespaceId": namespace_id,
            "overridesForwarders": overrides_forwarders,
        }
        response = self.http_get(self._url_for("/v3/api/sites"), params=params)
        return response.json()

    def get_v3_api_sites_by_id(self, site_id: str) -> dict:
        """
        Return information of the site that matches the specified site ID.

        :param site_id: The ID of the site.
        :return: Information of the site including: id, name, location, settings, registeredServicePointCount,
            updateStatus, updateInitiatedTime, version, blockedServicePointIds

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                site_id = '3f76fe19-900d-47ff-b00c-c3cab6f40903'         # Site ID

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v3_api_sites_by_id(site_id=site_id)

                print(result)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v3/api/sites/" + site_id))
        return response.json()

    def patch_v3_api_sites(self, payload: list[dict]):
        """
        Update the service point version of specified sites.

        .. note:: You must disable the automatic service point updates to use this API.

        :param payload: A list of the sites whose service points should be updated. It is
            possible to exclude certain service points from the operation. Each
            item in the list represents a site and options for it.

        Example:

            .. code-block:: python

                from bluecat_libraries.edge.api import EdgeClient

                payload = [
                    {
                        "id": "33709b0b-d429-45f1-8c82-51b2942a9133",
                        "version": "3.0.5",
                        "blockedServicePointIds": [
                            "feac4ad6-adb6-4c8d-924e-d314d29ec96d",
                            "91cbda2f-ac60-4a32-bc9f-02161e532b2d"]
                    },
                    {
                        "id": "aaa0830d-4639-4210-9158-0ac6395e2396",
                        "version": "3.0.6"
                    }
                ]

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.patch_v3_api_sites(payload)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        self.http_patch(
            self._url_for("/v3/api/sites"), json=payload, expected_status_codes=(codes.no_content,)
        )

    def post_v3_api_sites(self, payload: dict) -> str:
        """
        Create a new site.

        :param payload: Payload used to create a site.
        :return: The ID of the created site.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                payload = {
                    "name": "<site-name>",
                    "location": {
                    "address": "<address>"
                    }
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.post_v3_api_sites(payload=payload)

                print(result)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_post(
            self._url_for("/v3/api/sites"), json=payload, expected_status_codes=(codes.created,)
        )
        site_id = response.headers["Location"].rsplit("/", 1)[-1]
        return site_id

    def put_v3_api_sites(self, site_id: str, payload: dict):
        """
        Update an existing site. Note that all the parameters are updated with this
        action, whether you specify the values or not. If you leave a parameter
        out, its value will be overwritten with no data.

        :param site_id: The ID of the site.
        :param payload: Site parameters and their new values.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                site_id = "28c1b312-55e0-4dc4-8253-de7ae37db25d"
                payload = {
                    "name": "the new site name",
                    "location": {
                         "address": "123 Main St., Toronto",
                         "lng": "-79.3756671",
                         "lat": "43.6421529"
                     }
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.put_v3_api_sites(site_id, payload)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        self.http_put(
            self._url_for("/v3/api/sites/") + site_id,
            json=payload,
            expected_status_codes=(codes.no_content,),
        )

    def delete_v3_api_sites(self, site_id: str):
        """
        Delete the site specified by the site ID.

        :param site_id: The ID of the site to delete.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                site_id = "<site_id>"

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.delete_v3_api_sites(site_id=site_id)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        self.http_delete(
            self._url_for("/v3/api/sites/" + site_id), expected_status_codes=(codes.no_content,)
        )

    def post_v3_api_sites_clearcache(self, site_id: str):
        """
        Clear the cache of a site.

        :param site_id: The ID of the site.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                site_id = "28c1b312-55e0-4dc4-8253-de7ae37db25d"

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.post_v3_api_sites_clearcache(site_id)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        self.http_post(
            self._url_for("/v3/api/sites/" + site_id + "/clearCache"),
            expected_status_codes=(codes.accepted,),
        )

    # endregion

    # region Site Groups Administration
    def get_v1_api_customer_sitesandsitegroups_search(
        self, name_contains: str = None, desired_result_count: int = None
    ) -> list[dict]:
        """
        Return a list of the sites that match the specified search string.

        :param name_contains: Search for site and site group names which contain the specified string.
        :param desired_result_count: The maximum number of records to return.
        :return: A list of the sites that match the specified search string.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                name_contains = "test"         # search key word
                desired_result_count = 10      # max number of records to return

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_customer_sitesandsitegroups_search(name_contains=name_contains,
                                                                              desired_result_count=desired_result_count)

                for s in result:
                    print(s)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_get(
            self._url_for("/v1/api/customer/sitesAndSiteGroups/search"),
            params={"nameContains": name_contains, "desiredResultCount": desired_result_count},
        )
        return response.json()

    def post_v1_api_customer_sitegroups_create(self, payload: dict) -> dict:
        """
        Create a new site group with the sites specified by site ID.

        :param payload: Payload used to create a site group.
        :return: The details of the site group created.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient
                payload = {
                    "name":"name",
                    "description":"description",
                    "siteIds":["id1","id2"]
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.post_v1_api_customer_sitegroups_create(payload=payload)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_post(self._url_for("/v1/api/customer/siteGroups/create"), json=payload)
        return response.json()

    def post_v1_api_customer_sitegroups_delete(self, site_group_id: int):
        """
        Delete the site group specified by site group ID.

        :param site_group_id: The ID of the site group.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                site_group_id = 2

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.post_v1_api_customer_sitegroups_delete(site_group_id=site_group_id)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        self.http_post(
            self._url_for("/v1/api/customer/siteGroups/" + str(site_group_id) + "/delete")
        )

    def post_v1_api_customer_sitegroups_update(self, site_group_id: int, payload: dict):
        """
        Update the site group specified by site group ID with the new name, description, or sites.

        :param site_group_id: The ID of the site group.
        :param payload: Payload used to update the site group.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                site_group_id = 2
                payload = {
                    "name":"name",
                    "description":"description",
                    "siteIds":["id1","id2"]
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.post_v1_api_customer_sitegroups_update(site_group_id=site_group_id, payload=payload)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        self.http_post(
            self._url_for("/v1/api/customer/siteGroups/" + str(site_group_id) + "/update"),
            json=payload,
        )

    def get_v1_api_customer_sitegroups(self) -> list[dict]:
        """
        Gets a list of the site groups.

        :return: A list of all site groups.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_customer_sitegroups()

                for sp in result:
                    print(sp)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/customer/siteGroups"))
        return response.json()

    # endregion

    # region API Access Key Set
    def get_v1_api_apikeys(self) -> list[dict]:
        """
        Return the API access key sets for the current user.

        :return: API access key sets for the current user.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    results = client.get_v1_api_apikeys()

                for result in results:
                    print(result)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/apiKeys"))
        return response.json()

    def post_v1_api_apikeys(self) -> dict:
        """
        Create an API access key set for the current user.

        :return: Dictionary containing clientId and clientSecret that is created.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    api_key = client.post_v1_api_apikeys()

                print(api_key)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_post(self._url_for("/v1/api/apiKeys"))
        return response.json()

    def delete_v1_api_apikey_by_id(self, client_id: str):
        """
        Delete the API access key set with the specified client ID for the current user.

        :param client_id: The client id that needs to be deleted.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.delete_v1_api_apikey_by_id(<client_id>)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        self.http_delete(self._url_for("/v1/api/apiKeys/{id}".format(id=client_id)))

    def delete_v1_api_apikey(self, email_address: str):
        """
        Delete all the API access key sets for the specified email address.

        :param email_address: Delete all the API access key sets associated with this email address

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.delete_v1_api_apikey(<email_address>)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        self.http_delete(
            self._url_for("/v1/api/apiKeys"),
            params={"email_address": email_address},
            expected_status_codes=(codes.no_content,),
        )

    # endregion

    # region Service Point Versions
    def get_v1_api_spversions(self) -> list[str]:
        """
        Return a list of available service point versions, listed from the most recently released version to the oldest
        supported version.

        :return: A list of available service point versions.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_spversions()

                for ver in result:
                    print(ver)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/spVersions"))
        return response.json()

    # endregion

    # region Domain Lists
    def get_v2_domainlists(self, name_contains: Optional[str] = None) -> list[dict]:
        """
        Return a list of domain lists (that match the specified search string).

        :param name_contains: Search for domains which contain the specified string.
        :return: A list of domain lists (that match the specified search string).

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v2_domainlists()

                for r in result:
                    print(r)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_get(
            self._url_for("/v2/domainLists"), params={"nameContains": name_contains}
        )
        return response.json()

    def post_v2_domainlists(self, payload: dict) -> str:
        """
        Create a domain list.

        :param payload: Payload used to create a domain list.
        :return: The ID of a new domain list.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                payload = {
                    "name": "<domain-list-name>",
                    "description": "<domain-list-description>",
                    "sourceType": "user"
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.post_v2_domainlists(payload=payload)

                print(result)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_post(
            self._url_for("/v2/domainLists"), json=payload, expected_status_codes=(codes.created,)
        )
        domain_list_id = response.headers["Location"].rsplit("/", 1)[-1]
        return domain_list_id

    def delete_v2_domainlists(self, domain_list_id: str):
        """
        Delete the domain list specified by the domain list ID.

        :param domain_list_id: Payload used to create a domain list.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                domain_list_id = "<domain_list_id>"

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.delete_v2_domainlists(domain_list_id=domain_list_id)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        self.http_delete(
            self._url_for("/v2/domainLists/" + domain_list_id),
            expected_status_codes=(codes.no_content,),
        )

    def get_v2_domainlists_by_id(self, domain_list_id: str) -> dict:
        """
        Return a specific domain list.

        :param domain_list_id: The ID of the domain list to return.
        :return: Information of the domain list (that matches the given id) including: id, name, description,
            sourceType, domainCount, etc.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                domain_list_id = "<domain_list_id>"

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v2_domainlists_by_id(domain_list_id=domain_list_id)

                print(result)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v2/domainLists/" + domain_list_id))
        return response.json()

    def put_v2_domainlists(self, domain_list_id: str, domain_names: list):
        """
        Replace all domains within a domain list by supplying a list of domain names.

        :param domain_list_id: The ID of the domain list to update.
        :param domain_names: The names of domains to replace existing with.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                domain_list_id = "<domain_list_id>"
                domain_names = ["name-001", "name-002"]

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.put_v2_domainlists(domain_list_id=domain_list_id, domain_names=domain_names)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        data = "\n".join(domain_names)
        self.http_put(
            self._url_for("/v2/domainLists/" + domain_list_id),
            data=data,
            expected_status_codes=(codes.no_content,),
        )

    def patch_v2_domainlists(
        self,
        domain_list_id: str,
        domain_names_add: Optional[list] = None,
        domain_names_remove: Optional[list] = None,
    ):
        """
        Update the content of an existing domain list by adding or deleting domain names.

        :param domain_list_id: The ID of the domain list to update.
        :param domain_names_add: The names of domains to add to the domain list.
        :param domain_names_remove: The names of domains to remove from the domain list.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                domain_list_id = "<domain_list_id>"
                domain_names_add = ["name-001", "name-002"]
                domain_names_remove = ["name-003", "name-004"]

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.patch_v2_domainlists(domain_list_id=domain_list_id, domain_names_add=domain_names_add,
                                                domain_names_remove=domain_names_remove)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        if domain_names_add is None:
            domain_names_add = []
        if domain_names_remove is None:
            domain_names_remove = []
        data = "\n".join(domain_names_add)
        if domain_names_remove:
            data = [data, "-", *domain_names_remove]
            data = "\n".join(data)
        self.http_patch(
            self._url_for("/v2/domainLists/" + domain_list_id),
            data=data,
            expected_status_codes=(codes.no_content,),
        )

    def get_v1_api_list_dns_by_id(self, domain_list_id: str) -> list:
        """
        Return a list of domain lists.

        :param domain_list_id: The ID of the domain list.
        :return: Domain names of the given domain list.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                domain_list_id = '3f76fe19-900d-47ff-b00c-c3cab6f40903'         # domain list ID

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.v1_api_list_dns_by_id(domain_list_id=domain_list_id)

                for r in result:
                    print(r)

        .. versionadded:: 20.6.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/list/dns/" + domain_list_id))
        return response.text.strip("\n").split("\n")

    def get_v1_api_list_dns(self) -> list:
        """
        Return a list of domain lists.

        :return: A list of domain lists

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient


                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_list_dns()

                for r in result:
                    print(r)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/list/dns"))
        return response.json()

    def post_v1_api_list_dns(self, payload: dict) -> dict:
        """
        Create a domain list.

        :param payload: Payload used to create a domain list.
        :return: The created domain list.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                payload = {
                    "name": "<domain-list-name>",
                    "description": "<domain-list-description>",
                    "sourceType": "user"
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.post_v1_api_list_dns(payload=payload)

                print(result)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_post(self._url_for("/v1/api/list/dns"), json=payload)
        return response.json()

    def post_v1_api_list_dns_sourceconfiguration(self, domain_list_id: str, payload: dict):
        """
        Create a domain list sourced and dynamically updated from a local feed.

        :param domain_list_id: The ID of the domain list.
        :param payload: Source configuration payload.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                payload = {
                            "hostName":"source.host.name.org",
                            "privateKey":"privateKey",
                            "filePath":"/location/location",
                            "port":22,
                            "transferType":"rsyncSSH",
                            "user":"userName",
                            "publicHostKey":"publicKey",
                            "syncRate":5
                        }
                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.post_v1_api_list_dns_sourceconfiguration(<domain_list_id>, payload)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        self.http_post(
            self._url_for(f"/v1/api/list/dns/{domain_list_id}/sourceConfiguration"), json=payload
        )

    def post_v1_api_list_dns_attachfile(self, domain_list_id: str, file_handle: IO) -> dict:
        """
        Upload a CSV file containing a list of domain names to an existing DNS list.

        :param domain_list_id: The ID of the domain list.
        :param file_handle: File handle that contains the domains.
        :return: A dictionary containing a number of registered domains.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    with open('file.csv', 'r') as f:
                        client.authenticate(<client_id>, <client_secret>)
                        result = client.post_v1_api_list_dns_attachfile(<domain_list_id>, f)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_post(
            self._url_for(f"/v1/api/list/dns/{domain_list_id}/attachfile"),
            files={"file": ("file.txt", file_handle, "text/plain")},
        )
        return response.json()

    def post_v1_api_list_dns_delete(self, domain_list_id: str):
        """
        Delete the domain list specified by the domain list ID.

        :param domain_list_id: The ID of the domain list.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.post_v1_api_list_dns_delete(<domain_list_id>)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        self.http_post(self._url_for(f"/v1/api/list/dns/{domain_list_id}/delete"))

    def get_v1_api_list_dns_search(self, name_contains: str, desired_result_count: int):
        """
        Return a list of domain lists with names containing the search fragment, stopping when the desired
        result count reaches.

        :param name_contains: Filter based on the name.
        :param desired_result_count: The maximum number of returned results.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_list_dns_search(<name_contains>, 10)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(
            self._url_for("/v1/api/list/dns/search"),
            params={"nameContains": name_contains, "desiredResultCount": desired_result_count},
        )
        return response.json()

    # endregion

    # region Policy Management
    def get_v5_api_policies(
        self,
        site_id: Optional[str] = None,
        site_group_id: Optional[str] = None,
        domain_list_id: Optional[str] = None,
    ) -> list:
        """
        Get a list of all policies, or policies associated with a specified site, site group, or domain list.

        :param site_id: Specify a site by site ID to search for policies associated with a site.
        :param site_group_id: Specify a site group by site group ID to search for policies associated with a site group.
        :param domain_list_id: Specify a domain list by domain list ID to search for policies associated with a domain list.

        :return: A list of policies

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v5_api_policies()

                for r in result:
                    print(r)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(
            self._url_for("/v5/api/policies"),
            params={
                "siteId": site_id,
                "siteGroupId": site_group_id,
                "domainListId": domain_list_id,
            },
        )
        return response.json()

    def post_v5_api_policies(self, payload: dict) -> str:
        """
        Create a new policy.

        :param payload: Payload used to create a policy.

        :return: The ID of the created policy

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.post_v5_api_policies(<payload>)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_post(
            self._url_for("/v5/api/policies"), json=payload, expected_status_codes=(codes.created,)
        )
        policy_id = response.headers["Location"].split("/")[-1]
        return policy_id

    def get_v5_api_policies_by_id(self, policy_id: str) -> dict:
        """
        Search for a policy by policy ID.

        :param policy_id: Specify a policy by ID to return.

        :return: Policy for the given policy ID.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v5_api_policies_by_id(<policy_id>)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v5/api/policies/" + policy_id))
        return response.json()

    def delete_v5_api_policies(self, policy_id: str):
        """
        Delete the policy specified by the policy ID.

        :param policy_id: The ID of the policy to delete.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                policy_id = "<policy_id>"

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.delete_v5_api_policies(policy_id)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        self.http_delete(
            self._url_for("/v5/api/policies/" + policy_id),
            expected_status_codes=(codes.ok, codes.no_content),
        )

    def put_v5_api_policies(self, policy_id: str, payload: dict):
        """
        Update the policy specified by the policy ID. Note that all the fields are updated with this action,
        whether you specify any values or not. If you leave a field out, it's value will be overwritten with no data.

        :param policy_id: The ID of the policy to update.
        :param payload: Payload used to update the policy.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                policy_id = "<policy_id>"

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.put_v5_api_policies(policy_id, <payload>)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        self.http_put(
            self._url_for("/v5/api/policies/" + policy_id),
            json=payload,
            expected_status_codes=(codes.ok, codes.no_content),
        )

    # endregion

    # region Namespaces
    def get_v1_api_namespaces(self, site_id: str = "") -> list[dict]:
        """
        Return a list of namespaces, or namespaces associated with the site specified by site ID, if specified.

        :param site_id: The ID of the site.
        :return: The namespaces (all or those associated with the given site).

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_namespaces()

                for ns in result:
                    print(ns)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/namespaces"), params={"siteId": site_id})
        return response.json()

    def get_v1_api_namespaces_by_id(self, namespace_id: str) -> dict:
        """
        Return information of the namespace that matches the specified namespace ID.

        :param namespace_id: The ID of the namespace.
        :return: Information of the namespace including: id, name, description, forwarders, matchLists, exceptionLists,
            isDefault, associatedSiteSettings, ttl, umbrellaIntegrationId, latency

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                namespace_id = <namespace_id>

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_namespaces_by_id(namespace_id=namespace_id)

                print(result)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/namespaces/" + namespace_id))
        return response.json()

    def post_v1_api_namespaces(self, payload: dict) -> str:
        """
        Create a namespace.

        :param payload: Payload used to create a namespace.
        :return: The ID of the created namespace.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                payload = {
                   "name": "namespace",
                   "description": "this is a namespace",
                   "forwarders": ["8.8.8.8", "2.2.2.2"],
                   "matchLists": ["domainListId1", "domainListId2"],
                   "exceptionLists": ["domainListId1", "domainListId2"],
                   "umbrellaIntegrationId": "<id of umbrella integration>",
                   "ttl": 60
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.post_v1_api_namespaces(payload=payload)

                print(result)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_post(
            self._url_for("/v1/api/namespaces"),
            json=payload,
            expected_status_codes=(codes.created,),
        )
        namespace_id = response.headers["Location"].rsplit("/", 1)[-1]
        return namespace_id

    def put_v1_api_namespaces(self, namespace_id: str, payload: dict):
        """
        Update the namespace specified by the namespace ID. Note that all the fields are updated with this action, whether
        you specify values or not. If you leave a field out, its value will be overwritten with no data.

        :param namespace_id: The ID of the namespace to update.
        :param payload: Payload used to update a namespace.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                namespace_id = <namespace_id>
                payload = {
                   "name": "namespace",
                   "description": "this is a namespace",
                   "forwarders": ["8.8.8.8", "2.2.2.2"],
                   "matchLists": ["domainListId1", "domainListId2"],
                   "exceptionLists": ["domainListId1", "domainListId2"],
                   "umbrellaIntegrationId": "<id of umbrella integration>",
                   "ttl": 60
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.put_v1_api_namespaces(namespace_id=namespace_id, payload=payload)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        self.http_put(
            self._url_for("/v1/api/namespaces/" + namespace_id),
            json=payload,
            expected_status_codes=(codes.no_content,),
        )

    def patch_v1_api_namespaces(self, namespaces: list[dict]):
        """
        Set (up to three) namespaces as defaults.

        :param namespaces: List of namespace names and flags.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                namespaces = [
                    {
                        "id": "<id of the namespace>",
                        "isDefault": "true" or "false"
                    },
                    {
                        "id": "<id of the other namespace>",
                        "isDefault": "true" or "false"
                    }
                ]

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.patch_v1_api_namespaces(namespaces=namespaces)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        self.http_patch(
            self._url_for("/v1/api/namespaces"),
            json=namespaces,
            expected_status_codes=(codes.no_content,),
        )

    def delete_v1_api_namespaces(self, namespace_id: str):
        """
        Delete the namespace specified by the namespace ID.

        :param namespace_id: The ID of the namespace to delete.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                namespace_id = <namespace_id>

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.delete_v1_api_namespaces(namespace_id=namespace_id)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        self.http_delete(
            self._url_for("/v1/api/namespaces/" + namespace_id),
            expected_status_codes=(codes.no_content,),
        )

    # endregion

    # region Terms of Service
    def get_v1_api_tos(self):
        """
        Return the name, user email address, and timestamp when the current user accepted their Terms of Service.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.get_v1_api_tos()

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/tos"))
        return response.json()

    # endregion

    # region DNS Query Logs
    def get_v3_api_dnsquerylogs(self, filters: Optional[dict] = None) -> list[dict]:
        """
        Return a list of all (or optionally filtered) logged DNS queries.

        :param filters: The filters to narrow down the search result. The following filters (optional) can be used:

            * site_id (string or list) - The ID of the site to query for logs.
            * batch_size (integer) - The maximum number of records to return. Default size is 400. The maximum
              configurable size is 10000.
            * key (string) - The record ID of the DNS query log record to receive older or newer records.
            * order (string) - Specify whether to retrieve results in descending (default) or ascending order.
            * start_time (string) - Filter results for a specific time period, include the start time,
              in milliseconds since the Unix Epoch.
            * end_time (string) - Filter results for a specific time period, include the end time,
              in milliseconds since the Unix Epoch.
            * has_matched_policy (bool) - If true, only the DNS queries matching policies will display.
            * source_ip (string) - Filter results for the specified source IP address.
            * query_type (string) - The query record type to search for.
            * query_name (string) - The domain name to search for queries.
            * policy_action (string) - If one or more policy actions are provided, then only the policies matching the
              actions are returned. Valid actions are allow, block, redirect, and monitor.
            * policy_name (string) - If a policy name is provided, then only the policies matching the name are returned.
            * policy_id (string): If a policy ID is provided, then only the policies matching the ID are returned.
            * threat_type (string) - Return queries that match the specified threat type.
              Valid threat types are DGA and DNS_TUNNELING.
            * threat_indicator (string) - Return queries that match the specified threat indicator.
              Valid threat indicators are ENTROPY, UNIQUE_CHARACTER, EXCEEDING_LENGTH, UNCOMMON_QUERY_TYPE,
              VOLUMETRIC_TUNNELING, SUSPECT_DNS, and SUSPECT_TLD.
            * response_code (string) - The response code of the DNS query.
            * protocol (string) - The protocol of the DNS query (usually UDP or TCP).
            * namespace_id (string) - The ID of namespaces a DNS query was queried against.

        :return: The DNS queries (all or filtered).

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                filters = {
                    "site_id": [<site_id_1>, <site_id_2>],
                    "source_ip": "172.17.149.40"
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v3_api_dnsquerylogs(filters=filters)

                for q in result:
                    print(q)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        if filters is None:
            filters = {}
        params = {}
        param_names = {
            "site_id": "siteId",
            "batch_size": "batchSize",
            "key": "key",
            "order": "order",
            "start_time": "startTime",
            "end_time": "endTime",
            "has_matched_policy": "hasMatchedPolicy",
            "source_ip": "sourceIp",
            "query_type": "queryType",
            "query_name": "queryName",
            "policy_action": "policyAction",
            "policy_name": "policyName",
            "policy_id": "policyId",
            "threat_type": "threatType",
            "threat_indicator": "threatIndicator",
            "response_code": "responseCode",
            "protocol": "protocol",
            "namespace_id": "namespaceId",
        }

        for k in filters:
            if k in param_names and filters[k]:
                if isinstance(filters[k], list):
                    val = list(map(str, filters[k]))
                elif isinstance(filters[k], bool):
                    val = "true" if filters[k] else "false"
                else:
                    val = str(filters[k])
                params[param_names[k]] = val

        response = self.http_get(self._url_for("/v3/api/dnsQueryLogs"), params=params)
        return response.json()

    def get_v3_api_dnsquerylogs_by_id(self, query_id: str) -> dict:
        """
        Return the details for a specific query.

        :param query_id: The ID of the query.
        :return: Information of the DNS query including: time, source, siteId, query, queryType, response, id,
            actionTaken, matchedPolicies, authority, queryProtocol, threats, queriedNamespaces, latency

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                query_id = <query_id>

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v3_api_dnsquerylogs_by_id(query_id=query_id)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v3/api/dnsQueryLogs/" + query_id))
        return response.json()

    def get_v2_api_customer_dnsquerylog_count(self, site_name: str) -> dict:
        """
        Returns the total count of logged DNS queries within 30 days for the specified site name.

        :param site_name: Site name to search for the count of DNS query logs
        :return: Count of logged DNS queries within 30 days for the specified site name.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                site_name = <site_name>

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v2_api_customer_dnsquerylog_count(site_name=site_name)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(
            self._url_for("/v2/api/customer/dnsQueryLog/count"), params={"siteName": site_name}
        )
        return response.json()

    # endregion

    # region Settings
    def get_v1_api_settings(self):
        """
        Retrieve the automatic service point update settings.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    api_settings = client.get_v1_api_settings()

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/settings"))
        return response.json()

    def put_v1_api_settings(self, payload: dict):
        """
        Update the automatic service point update settings.

        :param payload: API parameters and their values

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                payload = {
                    "spAutomaticUpdatesEnabled": "true" or "false"
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.put_v1_api_settings(payload)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        self.http_put(
            self._url_for("/v1/api/settings"),
            json=payload,
            expected_status_codes=(codes.no_content,),
        )

    # endregion

    # region System Lists
    def get_v1_api_list_system(self, list_name: str) -> list:
        """
        Return the specified system-maintained domain lists, including all of the domains in the list,
        and the last time each listed domain incurred DNS traffic identifying it as suspected tunneling.

        :param list_name: The name of the list
        :return: The list of all the domains and the last time each listed domain incurred DNS traffic.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                query_id = <query_id>

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_list_system('tunneling')

                print(result)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/list/system/" + list_name))
        return response.json()

    def get_v1_api_list_system_content(self, list_name: str) -> str:
        """
        Return the contents of the specified system-maintained domain lists in JSON or CSV format. Leave out the
        Accept parameter to retrieve a CSV list instead of JSON.
        For each domain, the last time the domain incurred DNS traffic identifying it as a suspect for tunneling,
        and the time when that domain clears from the list according to the system-level set TTL,
        are returned.

        :param list_name: The name of the list
        :return: The contents of the specified system-maintained domain lists.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                query_id = <query_id>

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_list_system_content('tunneling')

                print(result)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/list/system/content/" + list_name))
        return response.text

    def get_v1_api_list_system_information(self, list_name: str) -> dict:
        """
        Return the meta information for the specified system-maintained domain list.

        :param list_name: The name of the list
        :return: The system-maintained domain list meta information.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                query_id = <query_id>

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_list_system_information('tunneling')

                print(result)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/list/system/information/" + list_name))
        return response.json()

    # endregion

    def get_v2_api_spimage_config(self, site_id: str) -> str:
        """
        Download the base64 encoded service point configuration information, including:

         - the endpoint to connect to for registration
         - the certificate that the service point uses to authenticate to its endpoint
         - the service point manager endpoint

        :param site_id: The id of the site
        :return: The base64 encoded service point configuration information.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                site_id = <site_id>

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v2_api_spimage_config(site_id=site_id)

                print(result)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v2/api/spImage/" + site_id + "/config"))
        return response.text

    def post_v2_api_spimage_generate(self, payload: dict):
        """
        Retrieve an OVA image of the specified site.

        :param payload: Payload (that contains site id) used to generate the OVA image.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                payload = {
                    "siteId": <site_id>
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.post_v2_api_spimage_generate(payload=payload)

                print(result)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        self.http_post(self._url_for("/v2/api/spImage/generate"), json=payload)

    def get_v2_api_spimage_status(self, site_id: str) -> dict:
        """
        Retrieve the status of the image generation.

        :param site_id: The id of the site
        :return: The status of the image generation along with other information.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                site_id = <site_id>

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v2_api_spimage_status(site_id=site_id)

                print(result)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v2/api/spImage/" + site_id + "/status"))
        return response.json()

    def post_v1_api_list_dns_update(self, domain_list_id: str, payload: dict):
        """
        Update a domain list name, description, or source type.

        :param domain_list_id: The ID of the domain list to update.
        :param payload: Payload used to update the domain list.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                domain_list_id = "<domain_list_id>"
                payload = {
                   "name": "new domain list name",
                   "description": "new domain list description",
                   "sourceType": "dynamic"
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.post_v1_api_list_dns_update(domain_list_id, payload)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        self.http_post(
            self._url_for("/v1/api/list/dns/" + domain_list_id + "/update"), json=payload
        )

    # region Users
    def get_v1_api_users(self) -> list[dict]:
        """
        Return the list of users.

        :return: A list of all users.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.get_v1_api_users()

                for user in result:
                    print(user)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_get(self._url_for("/v1/api/users"))
        return response.json()

    def post_v1_api_users(self, payload: dict) -> str:
        """
        Create a new user. An email is sent to the user with a temporary
        password and instructions on how to log in and set a new password.

        :param payload: Values for the user fields.
        :return: The ID of the created user.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                payload = {
                    "email": "email address",
                    "name": "first and last name",
                    "role": "SYSADMIN | ADMIN | ANALYST",
                    "status": "active | inactive"
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    result = client.post_v1_api_users(payload=payload)

                print(result)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        response = self.http_post(
            self._url_for("/v1/api/users"), json=payload, expected_status_codes=(codes.created,)
        )
        user_id = response.headers["Location"].rsplit("/", 1)[-1]
        # The user ID is known to contain a pipe character, which is URL-encoded
        # as "%7C" and needs to be unquoted.
        user_id = urllib.parse.unquote(user_id)
        return user_id

    def put_v1_api_users(self, user_id: str, payload: dict) -> dict:
        """
        Update the email address, name, role, and status of the user specified
        by the user ID.

        :param user_id: ID of the user to update.
        :param payload: Values for the user fields.
        :return: The updated user.

        .. note:: You can't update the email address of other users. You can
            only update your email address.

        Example:

            .. code:: python

                from bluecat_libraries.edge.api import EdgeClient

                user_id = <user_id>
                payload = {
                    "email":"new email address",
                    "name":"new name",
                    "role":"ADMIN | ANALYST",
                    "status":"active | inactive"
                }

                with EdgeClient(<edge_ci_url>) as client:
                    client.authenticate(<client_id>, <client_secret>)
                    client.put_v1_api_users(user_id=user_id, payload=payload)

        .. versionadded:: 20.12.1
        """
        self._require_auth()
        # The user ID is known to contain a pipe character, which needs to be
        # URL-encoded as "%7C" before being used in the URL.
        user_id = urllib.parse.quote(user_id)
        response = self.http_put(
            self._url_for("/v1/api/users/" + user_id),
            json=payload,
            expected_status_codes=(codes.ok,),
        )
        return response.json()

    # endregion Users
