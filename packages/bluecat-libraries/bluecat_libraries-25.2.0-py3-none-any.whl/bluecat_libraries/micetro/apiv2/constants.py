# Copyright 2024 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Values for Client V2 in Micetro."""


class MediaType:
    """Values for the media type in header"""

    JSON = "application/json"
    XML = "application/xml"


class ResponseMessage:
    """Values for the response message returned by Micetro REST API"""

    INVALID_USERNAME_OR_PASSWORD = "Invalid username or password."
    MISSING_SESSION_ID = "Missing Session ID."
