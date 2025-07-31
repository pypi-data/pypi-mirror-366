# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Values used in POST /v1/addServer method in BlueCat Address Manager."""
from ._enum import StrEnum


class ServerCapabilityProfiles(StrEnum):
    """
    Values for types of server profiles in BlueCat Address Manager.

    Following changes to supported server profiles in Integrity 9.6.0,
    some profiles in this class are not supported as of Integrity 9.6.0+.
    Others were introduced, and are only supported with Integrity 9.6.0+.

    Below is a table that lists which profiles are compatible with which Integrity
    versions

    .. list-table::
        :header-rows: 1

        * - Profile name
          - Supported prior to 9.6.0
          - Supported by 9.6.0 and later
        * - ADONIS_800
          - Yes
          - No
        * - ADONIS_1200
          - Yes
          - No
        * - ADONIS_1900
          - Yes
          - No
        * - ADONIS_1950
          - Yes
          - No
        * - ADONIS_1950
          - Yes
          - No
        * - ADONIS_XMB2
          - Yes
          - No
        * - ADONIS_XMB3
          - Yes
          - Yes
        * - AFILIAS_DNS_SERVER
          - Yes
          - Yes
        * - BLUECAT_ENTERPRISE
          - No
          - Yes
        * - BLUECAT_CORE
          - No
          - Yes
        * - BLUECAT_BRANCH_H
          - No
          - Yes
        * - BLUECAT_BRANCH_L
          - No
          - Yes
        * - DNS_DHCP_SERVER_20
          - Yes
          - Yes
        * - DNS_DHCP_SERVER_45
          - Yes
          - Yes
        * - DNS_DHCP_SERVER_60
          - Yes
          - Yes
        * - DNS_DHCP_SERVER_100
          - Yes
          - Yes
        * - DNS_DHCP_SERVER_100_D
          - Yes
          - Yes
        * - DNS_DHCP_GEN4_2000
          - Yes
          - Yes
        * - DNS_DHCP_GEN4_4000
          - Yes
          - Yes
        * - DNS_DHCP_GEN4_5000
          - Yes
          - Yes
        * - DNS_DHCP_GEN4_7000
          - Yes
          - Yes
        * - LEGACY
          - No
          - Yes
        * - OTHER_DNS_SERVER
          - Yes
          - Yes

    All profiles that were removed with Integrity 9.6.0+ are replaced with
    the ``LEGACY`` profile, which represents any device that now doesn't have a supported
    profile.
    """

    ADONIS_800 = "ADONIS_800"  # replaced with "LEGACY" as of Integrity 9.6.0
    ADONIS_1200 = "ADONIS_1200"  # replaced with "LEGACY" as of Integrity 9.6.0
    ADONIS_1900 = "ADONIS_1900"  # replaced with "LEGACY" as of Integrity 9.6.0
    ADONIS_1950 = "ADONIS_1950"  # replaced with "LEGACY" as of Integrity 9.6.0
    ADONIS_XMB2 = "ADONIS_XMB2"  # replaced with "LEGACY" as of Integrity 9.6.0
    ADONIS_XMB3 = "ADONIS_XMB3"
    AFILIAS_DNS_SERVER = "AFILIAS_DNS_SERVER"
    BLUECAT_ENTERPRISE = "BLUECAT_ENTERPRISE"  # new in Integrity 9.6.0
    BLUECAT_CORE = "BLUECAT_CORE"  # new in Integrity 9.6.0
    BLUECAT_BRANCH_H = "BLUECAT_BRANCH_H"  # new in Integrity 9.6.0
    BLUECAT_BRANCH_L = "BLUECAT_BRANCH_L"  # new in Integrity 9.6.0
    DNS_DHCP_SERVER_20 = "DNS_DHCP_SERVER_20"
    DNS_DHCP_SERVER_45 = "DNS_DHCP_SERVER_45"
    DNS_DHCP_SERVER_60 = "DNS_DHCP_SERVER_60"
    DNS_DHCP_SERVER_100 = "DNS_DHCP_SERVER_100"
    DNS_DHCP_SERVER_100_D = "DNS_DHCP_SERVER_100_D"
    DNS_DHCP_GEN4_2000 = "DNS_DHCP_GEN4_2000"
    DNS_DHCP_GEN4_4000 = "DNS_DHCP_GEN4_4000"
    DNS_DHCP_GEN4_5000 = "DNS_DHCP_GEN4_5000"
    DNS_DHCP_GEN4_7000 = "DNS_DHCP_GEN4_7000"
    LEGACY = "LEGACY"  # new in Integrity 9.6.0, catchall for legacy devices
    OTHER_DNS_SERVER = "OTHER_DNS_SERVER"
