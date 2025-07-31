..
    Copyright 2021-2023 BlueCat Networks (USA) Inc. and its affiliates.
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.

BlueCat Libraries
=================

Modules for working with products from BlueCat Networks.

The Python clients in this package provide access to the following BlueCat HTTP APIs:

-   Address Manager RESTful v2 API (9.5)
-   Address Manager Legacy REST v1 API (9.3, 9.4, 9.5)
-   Address Manager Failover API
-   DNS Edge API
-   Micetro REST API

.. note::

    BlueCat strongly recommends using the RESTful v2 API instead of the Legacy v1 API.
    The RESTful v2 API strictly adheres to HTTP 1.1 constraints as detailed in RFC 2616,
    and allows for cleaner, more understandable code.

The examples below illustrate how to use the Address Manager RESTful v2 API and Legacy v1
API to fetch BlueCat Address Manager (BAM) configurations.


Examples using Address Manager RESTful v2 API
---------------------------------------------

.. code-block:: python

    from bluecat_libraries.address_manager.apiv2 import Client, MediaType
    import csv

    # Retrieve the configurations. Request the data as per BAM's default content type.
    with Client(<bam_url>) as client:
        client.login(<username>, <password>)
        response = client.http_get("/configurations")
        configurations = response["data"]
        for configuration in configurations:
            print(f'{configuration["id"]}: {configuration["name"]}')
        client.logout()

    # Retrieve the configurations. Request that the response is in 'JSON' format.
    # The result should contain only fields 'id' and 'name'.
    with Client(<bam_url>) as client:
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
    with Client(<bam_url>) as client:
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


Example using Address Manager Legacy REST v1 API
------------------------------------------------

.. code-block:: python

    # Fetch all configurations from a BlueCat Address Manager server.

    from bluecat_libraries.address_manager.api import Client
    from bluecat_libraries.address_manager.constants import ObjectType

    with Client(<bam_url>) as client:
        client.login(<username>, <password>)
        configs = client.get_entities(0, ObjectType.CONFIGURATION)
        client.logout()

    for config in configs:
        print(config)


Examples using Micetro REST API
---------------------------------------------

.. code-block:: python

    from bluecat_libraries.micetro.apiv2 import Client, MediaType

    # Retrieve the users. Request the data as per Micetro's default content type.

    with Client(<micetro_url>) as client:
        client.authenticate(<username>, <password>)
        response = client.http_get("/users")
        users = response["result"]["users"]
        for user in users:
            print(f'{user["ref"]}: {user["name"]}')

    # Retrieve users. Request that the response is in 'XML' format.

    with Client(<micetro_url>) as client:
        client.authenticate(<username>, <password>)
        response = client.http_get("/users", headers={"Accept": MediaType.XML})
        print(response)


Note
----

Subpackage ``bluecat_libraries.address_manager.api.rest.provisional`` is a deprecated dependency of
BlueCat Gateway, and currently exists while we are still in the pre-deprecation-removal grace
period. It will be removed in the next release of BlueCat Libraries.
