# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Modules defining values used when working with BlueCat Address Manager."""
from bluecat_libraries.address_manager.constants.access_right_values import AccessRightValues
from bluecat_libraries.address_manager.constants.additional_ip_service_type import (
    AdditionalIPServiceType,
)
from bluecat_libraries.address_manager.constants.dhcp_custom_option_type import DHCPCustomOptionType
from bluecat_libraries.address_manager.constants.dhcp_define_range import DHCPDefineRange
from bluecat_libraries.address_manager.constants.dhcp_deployment_role_type import (
    DHCPDeploymentRoleType,
)
from bluecat_libraries.address_manager.constants.dhcp6_deployment_option_type import (
    DHCP6ClientDeploymentOptionType,
)
from bluecat_libraries.address_manager.constants.dhcp_match_class_criteria import DHCPMatchClass
from bluecat_libraries.address_manager.constants.dhcp_service import (
    DHCPServiceOption,
    DHCPServiceOptionConstant,
)
from bluecat_libraries.address_manager.constants.discovery_type import DiscoveryType
from bluecat_libraries.address_manager.constants.dns_deployment_role_type import (
    DNSDeploymentRoleType,
)
from bluecat_libraries.address_manager.constants.enum_service import EnumServices
from bluecat_libraries.address_manager.constants.ip_group_range_position import IPGroupRangePosition
from bluecat_libraries.address_manager.constants.object_type import ObjectType
from bluecat_libraries.address_manager.constants.option_type import OptionType
from bluecat_libraries.address_manager.constants.response_policy_type import ResponsePolicy
from bluecat_libraries.address_manager.constants.server_capability_profiles import (
    ServerCapabilityProfiles,
)
from bluecat_libraries.address_manager.constants.servers_deployment_status import (
    ServersDeploymentStatus,
    DeploymentTaskStatus,
)
from bluecat_libraries.address_manager.constants.snmp import SNMPVersion
from bluecat_libraries.address_manager.constants.traversal_method import TraversalMethod
from bluecat_libraries.address_manager.constants.user_defined_field_type import UserDefinedFieldType
from bluecat_libraries.address_manager.constants.user_defined_link_type import (
    UserDefinedLinkEntityType,
)
from bluecat_libraries.address_manager.constants.ip_assignment_action_values import (
    IPAssignmentActionValues,
)
from bluecat_libraries.address_manager.constants.ip_address_states import IPAddressState
from bluecat_libraries.address_manager.constants.vendor_profile_option_type import (
    VendorProfileOptionType,
)
from bluecat_libraries.address_manager.constants.zone_template_reapply_mode import (
    ZoneTemplateReapplyMode,
)
from bluecat_libraries.address_manager.constants.defined_probe import (
    DefinedProbeStatus,
    DefinedProbe,
)


__all__ = [
    "AccessRightValues",
    "AdditionalIPServiceType",
    "DefinedProbe",
    "DefinedProbeStatus",
    "DeploymentTaskStatus",
    "DHCP6ClientDeploymentOptionType",
    "DHCPCustomOptionType",
    "DHCPDefineRange",
    "DHCPDeploymentRoleType",
    "DHCPMatchClass",
    "DHCPServiceOption",
    "DHCPServiceOptionConstant",
    "DiscoveryType",
    "DNSDeploymentRoleType",
    "EnumServices",
    "IPAddressState",
    "IPAssignmentActionValues",
    "IPGroupRangePosition",
    "ObjectType",
    "OptionType",
    "ResponsePolicy",
    "ServerCapabilityProfiles",
    "ServersDeploymentStatus",
    "SNMPVersion",
    "TraversalMethod",
    "UserDefinedFieldType",
    "UserDefinedLinkEntityType",
    "VendorProfileOptionType",
    "ZoneTemplateReapplyMode",
]
