# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["AssetUpdateAttributesParams"]


class AssetUpdateAttributesParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    attributes: Required[object]
    """
    attributes can be used to add any useful information or context to your assets
    like the vehicle type, shift timing etc. These attributes can also be used to
    filter assets in **Search**, **Monitor**, and _Get Asset List_ queries.

    Provide the attributes to be added or updated, in key:value format. If an
    existing key is provided in the input, then the value will be modified as per
    the input value. If a new key is provided in the input, then the key would be
    added to the existing set. The contents of any value field are neither altered
    nor removed unless specifically referred to by its key in the input request.

    Please note that the maximum number of key:value pairs that can be added to an
    attributes object is 100. Also, the overall size of attributes object should not
    exceed 65kb.
    """
