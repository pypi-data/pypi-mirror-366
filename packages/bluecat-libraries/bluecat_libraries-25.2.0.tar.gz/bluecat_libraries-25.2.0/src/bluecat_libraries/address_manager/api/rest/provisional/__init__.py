# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Package for working with provisinal REST API"""
from bluecat_libraries.address_manager.api.rest.provisional.client import ProvisionalClient
from bluecat_libraries.address_manager.api.rest.provisional.rest_dict import RESTDict
from bluecat_libraries.address_manager.api.rest.provisional.rest_entity_array import RESTEntityArray
from bluecat_libraries.address_manager.api.rest.provisional.rest_fault import RESTFault

__all__ = [
    "ProvisionalClient",
    "RESTDict",
    "RESTEntityArray",
    "RESTFault",
]
