# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Modules for working with BlueCat Address Manager's API v2."""
from bluecat_libraries.address_manager.apiv2.client import Client
from bluecat_libraries.address_manager.apiv2.constants import MediaType
from bluecat_libraries.address_manager.apiv2.exceptions import BAMV2ErrorResponse

__all__ = ["BAMV2ErrorResponse", "Client", "MediaType"]
