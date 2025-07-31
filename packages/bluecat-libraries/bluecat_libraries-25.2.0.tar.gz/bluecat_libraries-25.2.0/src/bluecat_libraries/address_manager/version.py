# Copyright 2023-2024 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""
Utilities related to the version of BlueCat Address Manager.

.. versionadded:: 23.1.0
"""
import warnings
from bluecat_libraries.http_client.version import Version, parse_version

# Warn about the deprecation
warnings.warn(
    "This module is moved to `http_client` and might be removed in future versions. "
    "Please update your imports.",
    ImportWarning,
)

__all__ = ["Version", "parse_version"]
