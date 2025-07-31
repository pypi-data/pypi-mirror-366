# Copyright 2021-2022 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Models representing all Address Manager object types supported in the API."""
import copy
import json

from bluecat_libraries.address_manager.api.serialization import (
    deserialize_joined_key_value_pairs,
    serialize_joined_key_value_pairs,
    serialize_joined_values,
    serialize_possible_list,
    deserialize_possible_list,
)
from typing import Any, Optional  # pylint: disable=unused-import


class APIEntity(dict):
    """
    Model for the BAM API object type APIEntity.

    :key id: The entity's ID. Value type is int.
    :key name: The entity's name. Value type is str | None.
    :key type: The entity's type. Must be a valid BAM object type.
    :key properties: (Optional) Additional properties on the entity. Value must be dict[str, str].
    """

    @staticmethod
    def to_raw_model(data: dict[str, Any]) -> dict[str, str]:
        """
        :param data: APIEntity object or dict equivalent.
        :return: Dict that, once JSON-serialized, can be passed to BAM endpoints.
        """
        data = copy.deepcopy(data)
        data["properties"] = serialize_joined_key_value_pairs(data.get("properties"))
        return data

    @staticmethod
    def from_raw_model(data: dict[str, str]) -> "Optional[APIEntity]":
        """
        :param data: Dict obtained by JSON-deserializing an APIEntity returned by a BAM endpoint.
        :return: Entity object, or None if input's ``id`` is 0.
        """
        data = copy.deepcopy(data)
        if data["id"] == 0:
            return None
        data["properties"] = (
            deserialize_joined_key_value_pairs(data["properties"]) if data.get("properties") else {}
        )
        return APIEntity(data)


class APIAccessRight(dict):
    """
    Model for the BAM API object type APIAccessRight.

    :key entityId: ID of the object to which the access right applies. Value type is int. Must be greater than 0.
    :key userId: The access right's owner's ID. Value type is int. Must be greater than 0.
    :key value: Value must be "HIDE", "VIEW", "ADD", "CHANGE", or "FULL".
    :key overrides: (Optional) Override access rights of ``entityId``'s descendants (by default,
        they inherit ``entityId``'s access right). Value type is dict[str, str]. Keys are object
        types to be overriden; values are access right values.
    :key properties: (Optional) Additional properties on the access right. Value type is dict[str, str].
    """

    @staticmethod
    def to_raw_model(data: dict[str, Any]) -> dict[str, str]:
        """
        :param data: APIAccessRight object or dict equivalent.
        :return: Dict that, once JSON-serialized, can be passed to BAM endpoints.
        """
        data = copy.deepcopy(data)
        data["overrides"] = serialize_joined_key_value_pairs(data.get("overrides"))
        data["properties"] = serialize_joined_key_value_pairs(data.get("properties"))
        return data

    @staticmethod
    def from_raw_model(data: dict[str, str]) -> "APIAccessRight":
        """
        :param data: Dict obtained by JSON-deserializing an APIAccessRight returned by a BAM endpoint.
        :return: Access right object.
        """
        data = copy.deepcopy(data)
        data["overrides"] = (
            deserialize_joined_key_value_pairs(data["overrides"]) if data.get("overrides") else {}
        )
        data["properties"] = (
            deserialize_joined_key_value_pairs(data["properties"]) if data.get("properties") else {}
        )
        return APIAccessRight(data)


class APIDeploymentRole(dict):
    """
    Model for the BAM API object type APIDeploymentRole.

    :key id: The deployment role's ID. Value type is int.
    :key type: Value must be "NONE", "MASTER", "MASTER_HIDDEN", "SLAVE", "SLAVE_STEALTH", "FORWARDER", "STUB", "RECURSION", "PEER", or "AD MASTER".
    :key service: Value must be "DNS", "DHCP", or "TFTP".
    :key entityId: The deployed entity's ID. Value type is int. Must be greater than 0.
    :key serviceInterfaceId: ID of the server interface being deployed into. Value type is int. Must be greater than 0.
    :key properties: (Optional) Additional properties on the deployment role. Value type is dict[str, str].
    """

    @staticmethod
    def to_raw_model(data: dict[str, Any]) -> dict[str, str]:
        """
        :param data: APIDeploymentRole object or dict equivalent.
        :return: Dict that, once JSON-serialized, can be passed to BAM endpoints.
        """
        data = copy.deepcopy(data)
        data["properties"] = serialize_joined_key_value_pairs(data.get("properties"))
        return data

    @staticmethod
    def from_raw_model(data: dict[str, str]) -> "Optional[APIDeploymentRole]":
        """
        :param data: Dict obtained by JSON-deserializing an APIDeploymentRole returned by a BAM endpoint.
        :return: Deployment role object, or None if input's ``id`` is 0.
        """
        data = copy.deepcopy(data)
        if data.get("id") == 0:
            return None
        data["properties"] = (
            deserialize_joined_key_value_pairs(data["properties"]) if data.get("properties") else {}
        )
        return APIDeploymentRole(data)


class APIDeploymentOption(dict):
    """
    Model for the BAM API object type APIDeploymentOption.

    :key id: The deployment option's ID. Value type is int.
    :key type: The deployment option's type. Must be a valid BAM option type.
    :key name: The deployment option's name. Value type is str.
    :key value: Field values of the option. Value type is list[str].
    :key properties: (Optional) Additional properties on the deployment option. Value type is dict[str, str].
    """

    @staticmethod
    def to_raw_model(data: dict[str, Any]) -> dict[str, str]:
        """
        :param data: APIDeploymentOption object or dict equivalent.
        :return: Dict that, once JSON-serialized, can be passed to BAM endpoints.
        """
        data = copy.deepcopy(data)
        data["value"] = serialize_possible_list(data.get("value", ""))
        data["properties"] = serialize_joined_key_value_pairs(data.get("properties"))
        return data

    @staticmethod
    def from_raw_model(data: dict[str, str]) -> "Optional[APIDeploymentOption]":
        """
        :param data: Dict obtained by JSON-deserializing an APIDeploymentOption returned by a BAM endpoint.
        :return: Deployment role object, or None if input's ``id`` is 0.
        """
        data = copy.deepcopy(data)
        if data.get("id") == 0:
            return None
        data["value"] = deserialize_possible_list(data.get("value", ""))
        data["properties"] = (
            deserialize_joined_key_value_pairs(data["properties"]) if data.get("properties") else {}
        )
        return APIDeploymentOption(data)


class APIUserDefinedField(dict):
    """
    Model for the BAM API object type APIUserDefinedField.

    :key name: The UDF's unique name. Value type is str.
    :key displayName: The UDF's display name. Value type is str.
    :key type: The UDF's type. Must be a valid BAM UDF type.
    :key defaultValue: The UDF's default value. Value type is str.
    :key required: If true, users must enter data in the field. Value type is bool.
    :key hideFromSearch: If true, the UDF is hidden from search. Value type is bool.
    :key validatorProperties: (Optional) The UDF's validation properties. Value type is dict[str, str].
    :key predefinedValues: (Optional) The UDF's preset values. Value type is list[str].
    :key properties: (Optional) Additional properties on the UDF. Value type is dict[str, str].
    """

    @staticmethod
    def to_raw_model(data: dict[str, Any]) -> dict[str, str]:
        """
        :param data: APIUserDefinedField object or dict equivalent.
        :return: Dict that, once JSON-serialized, can be passed to BAM endpoints.
        """
        data = copy.deepcopy(data)
        data["predefinedValues"] = serialize_joined_values(
            data.get("predefinedValues"), item_sep="|"
        )
        data["validatorProperties"] = serialize_joined_key_value_pairs(
            data.get("validatorProperties"), item_sep=","
        )  # object types that can take multiple properties, separate each property with a “,” comma
        data["properties"] = serialize_joined_key_value_pairs(data.get("properties"))
        return data

    @staticmethod
    def from_raw_model(data: dict[str, str]) -> "APIUserDefinedField":
        """
        :param data: Dict obtained by JSON-deserializing an APIUserDefinedField returned by a BAM endpoint.
        :return: UDF object.
        """
        data = copy.deepcopy(data)

        if data.get("predefinedValues"):
            data["predefinedValues"] = list(filter(None, data.get("predefinedValues").split("|")))
        else:
            data["predefinedValues"] = []

        if data.get("validatorProperties"):
            data["validatorProperties"] = deserialize_joined_key_value_pairs(
                data.get("validatorProperties"), item_sep=","
            )
        else:
            data["validatorProperties"] = {}

        data["properties"] = (
            deserialize_joined_key_value_pairs(data["properties"]) if data.get("properties") else {}
        )
        return APIUserDefinedField(data)


class UDLDefinition(dict):
    """
    Model for the structure describing User-Defined Link definitions used by
    Address Manager's API.

    .. note:: Starting from Address Manager v9.4.0, the option **description** is supported.

        * The maximum length of this field is 512 characters.
        * If the **description** field is not specified, it will be null.
        * On upgrading from Address Manager v9.3.0, the **description** for the existing links will
          be populated as **null**.

    :key linkType: The UDL's unique name. Value type is str. Cannot be a reserved link type name
        and cannot start with "BCN\\_".
    :key displayName: The UDL's name as displayed in BAM. Value type is str.
    :key sourceEntityTypes: The UDL's source entity types. Value type is list[str].
    :key destinationEntityTypes: The UDL's destination entity types. Value type is list[str].
    :key description: (Optional) The description for the user-defined link.
    """

    # NOTE: The use of '\\_' in the above docstring is intentional. The goal is 2 level escaping:
    # 1) '\\' translates into '\' in the Python string
    # 2) '\_' make reStructuredText not treat 'BCN_' as an internal hyperlink target.

    @staticmethod
    def to_raw_model(data: dict[str, Any]) -> str:
        """
        :param data: UDLDefinition object or dict equivalent.
        :return: JSON-encoded string that can be passed to BAM endpoints.
        """
        return json.dumps(data)

    @staticmethod
    def from_raw_model(data: dict[str, str]) -> "UDLDefinition":
        """
        :param data: Dict obtained by JSON-deserializing a UDL returned by a BAM endpoint.
        :return: UDL definition object.
        """
        return UDLDefinition(data)


class UDLRelationship(dict):
    """
    Model for the structure describing User-Defined Link relationships used by
    Address Manager's API.

    .. note:: Starting from Address Manager v9.4.0, the option **description** and
        **destinationEntityIds** are supported.

    :key linkType: The UDL's link type. Value type is str.
    :key sourceEntityId: The UDL's source entity ID. Value type is int.
    :key description: (optional) The description for the user-defined link.
    :key destinationEntityId: (Optional) The UDL's destination entity ID. Value type is int.
    :key destinationEntityIds: (Optional) The list of UDL's destination entity ID, comma-separated
        inside square brackets.
    """

    @staticmethod
    def to_raw_model(data: dict[str, Any]) -> str:
        """
        :param data: UDLRelationship object or dict equivalent.
        :return: JSON-encoded string that can be passed to BAM endpoints.
        """
        return json.dumps(data)

    @staticmethod
    def from_raw_model(data: dict[str, str]) -> "UDLRelationship":
        """
        :param data: Dict obtained by JSON-deserializing the result of UDLRelationship.to_raw_model(<something>).
        :return: UDL relationship object.
        """
        return UDLRelationship(data)


class RetentionSettings(dict):
    """
    Model for BAM history retention settings.

    :key admin: (Optional) The number of days of administrative history to keep in the database. Value type is int.
    :key sessionEvent: (Optional) The number of days of session event history to keep in the database. Value type is int.
    :key ddns: (Optional) The number of days of DDNS history to keep in the database. Value type is int.
    :key dhcp: (Optional) The number of days of DHCP history to keep in the database. Value type is int.

    .. note::

        * The value for sessionEvent must be greater than or equal to the value of
          each of the other types.
        * The input value for the retention periods (in days) must be greater than or equal to one.
        * Setting the value to -1 is equivalent to Retain Indefinitely in the BAM database.
        * Setting the DDNS and DHCP retention setting to 0 is equivalent to Do Not Retain,
          and these records no longer write to the database.
          So, if a user has enabled the audit data export feature, they will get no records written to their audit data.
    """

    @staticmethod
    def to_raw_model(data: dict[str, Any]) -> dict:
        """
        :param data: RetentionSettings object or dict equivalent.
        :return: Dict that, once JSON-serialized, can be passed to BAM endpoints.
        """
        data = copy.deepcopy(data)
        update_admin = data.get("admin") is not None
        update_session_event = data.get("sessionEvent") is not None
        update_ddns = data.get("ddns") is not None
        update_dhcp = data.get("dhcp") is not None
        return {
            "admin": data.get("admin"),
            "updateAdmin": update_admin,
            "sessionEvent": data.get("sessionEvent"),
            "updateSessionEvent": update_session_event,
            "ddns": data.get("ddns"),
            "updateDdns": update_ddns,
            "dhcp": data.get("dhcp"),
            "updateDhcp": update_dhcp,
        }

    @staticmethod
    def from_raw_model(data: str) -> "RetentionSettings":
        """
        :param data: A value in the format returned by BAM method "updateRetentionSettings"
            that holds the ordered settings for: admin, sessionEvent, ddns, and dhcp.
        :return: Retention settings object.
        """
        admin, session_event, ddns, dhcp = list(map(int, data.split(",")))
        return RetentionSettings(
            admin=admin,
            sessionEvent=session_event,
            ddns=ddns,
            dhcp=dhcp,
        )


class ResponsePolicySearchResult(dict):
    """Model for the BAM API object type ResponsePolicySearchResult.

    :key configId: ID of the parent configuration in which the response policy item is configured. Value type is int.
    :key parentIds: IDs of parent response policy or response policy zone objects. Value type is list[int].
        If policy item is associated with a Response Policy, it is the Response Policy object ID.
        If policy item is associated with BlueCat Security feed data, it is the RP Zone object ID.
    :key name: The response policy item's name. Value type is str.
    :key category: The name of the BlueCat security feed category associated with the policy item. Value type is str | None.
    :key policyType: The response policy's type. Value type is str.
    """

    @staticmethod
    def from_raw_model(data: dict[str, str]) -> "ResponsePolicySearchResult":
        """
        :param data: Dict obtained by JSON-deserializing a ResponsePolicySearchResult returned by a BAM endpoint.
        :return: Response policy search result object.
        """
        data = copy.deepcopy(data)
        data["parentIds"] = list(map(int, data.get("parentIds").split(",")))
        return ResponsePolicySearchResult(data)


class APIData(dict):
    """
    Model for the BAM API object type APIData.

    :key name: The name of the probe to collect data. Value type is str.
    :key properties: Additional properties on the probe. Value must be list.
    """

    @staticmethod
    def from_raw_model(data: dict[str, str]) -> "APIData":
        """
        :param data: Dict obtained by JSON-deserializing an APIData returned by a BAM endpoint.
        :return: API Data object.
        """
        data = copy.deepcopy(data)
        data["properties"] = json.loads(data["properties"])
        return APIData(data)
