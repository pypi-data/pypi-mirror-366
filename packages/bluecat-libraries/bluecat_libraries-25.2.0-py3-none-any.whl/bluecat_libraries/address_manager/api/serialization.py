# Copyright 2020-2023 BlueCat Networks (USA) Inc. and its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# pylint: disable=C0112,C0115,C0116,W0511,W0613;
"""Functions related to the conversion of data to and from BlueCat Address Manager's API."""
import re
from typing import Union

from bluecat_libraries.http_client.exceptions import GeneralError


def deserialize_joined_key_value_pairs(value: str, item_sep="|", keyvalue_sep="=") -> dict:
    """Convert a single-string representation into a dictionary."""
    # NOTE: A straightforward "split by pipes and then split by equal signs" would cause erroneous interpretations,
    # because of the presence of escaped pipes in both names and values.
    # NOTE: Currently, equal signs are not escaped, although they may be present in both the name and the value of a
    # property. We can have "=====" as a key-value pair and no way of knowing is it "=" : "===", "==": "==", or
    # "===": "=". Thus, the first occurring equal sign is treated as a separator.
    properties = {}
    data = []
    is_escape = False
    key_name = None
    for char in value:
        if char == keyvalue_sep and not key_name:
            key_name = "".join(data)
            data = []
        elif char == item_sep and not is_escape:
            if key_name:
                properties[key_name] = "".join(data)
                key_name = None
            data = []
        elif char == "\\" and not is_escape:
            is_escape = True
            continue
        else:
            if is_escape and char != item_sep:
                data.append("\\")
            data.append(char)
        is_escape = False
    if key_name:
        properties[key_name] = "".join(data)
    return properties


def serialize_joined_key_value_pairs(values: dict, item_sep="|", keyvalue_sep="=") -> str:
    if not values:
        return ""

    result = item_sep.join(
        "{key}{keyvalue_sep}{value}".format(
            key=escape(check_allowed_condition(key)),
            keyvalue_sep=keyvalue_sep,
            value=escape(check_allowed_condition(str(value))),
        )
        for key, value in values.items()
    )
    return result + item_sep if result else ""


def serialize_joined_values(values: list, item_sep=",") -> str:
    if not values:
        return ""
    result = item_sep.join(str(x) for x in values)
    return result


def serialize_possible_list(value: Union[str, list[str], list[list[str]]]) -> str:
    """
    If ``value`` is a list, then either all inner elements must be lists, or no element can be a
    list. Otherwise, no behavior is guaranteed.
    """
    # Simple value case
    if not isinstance(value, list):
        return str(value)

    # Empty list case
    if not value:
        return ""

    # 1D case
    if not isinstance(value[0], list):
        return ",".join(str(x) for x in value)

    # 2D case
    out = []
    for inner in value:
        x = ",".join(str(x) for x in inner)
        out.append("{" + x + "}")
    return ",".join(out)


def deserialize_possible_list(value: str) -> Union[str, list[str], list[list[str]]]:
    # We rely on the fact that individual values do not contain `{`, `}`, or `,`

    # 2D case
    if value.startswith("{"):
        return [item.group(1).split(",") for item in re.finditer(r"{([^}]*)}", value)]

    # Empty string becomes [""]
    out = value.split(",")
    return out if len(out) > 1 else out[0]


def escape(value: str) -> str:
    return value.replace("|", "\\|")


def unescape(value: str) -> str:
    return value.replace("\\|", "|")


def check_allowed_condition(value: str) -> str:
    """
    Check whether the value is acceptable.

    :param value: The value to be checked.
    :raises GeneralError: If the value is not acceptable.
    """
    # NOTE: BAM API v1 uses the pipe character - "|" - as separator between
    # key-value pairs. Additionally, when the pipe character has to be present
    # in a value it is "escaped" by preceding it with a backslash - "\".
    # Because backslashes themselves are not escaped, if a value ends up with
    # one, then the API will consider the pipe as escaped. That would result in
    # the whole next key-value pair to be considered as part of the value of the
    # current pair.
    # Thus, to avoid creating values in BAM different from what the user
    # intended, we do not accept values to end with a backslash.
    if value.endswith("\\"):
        raise GeneralError("Backslash is not allowed at the end of a value.")
    return value
