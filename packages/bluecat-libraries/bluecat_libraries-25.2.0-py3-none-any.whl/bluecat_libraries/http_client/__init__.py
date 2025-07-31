# Copyright 2020-2024 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Module for providing base classes for clients."""
from bluecat_libraries.http_client.client import Client
from bluecat_libraries.http_client.exceptions import (
    GeneralError,
    ClientError,
    ErrorResponse,
    UnexpectedResponse,
)
from bluecat_libraries.http_client.instance import Instance
from bluecat_libraries.http_client.version import Version, parse_version


__all__ = [
    "Client",
    "ClientError",
    "ErrorResponse",
    "GeneralError",
    "Instance",
    "UnexpectedResponse",
    "Version",
    "parse_version",
]
