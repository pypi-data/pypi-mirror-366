# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

from .meta_data_param import MetaDataParam

__all__ = ["AssetUpdateParams"]


class AssetUpdateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    cluster: Literal["america"]
    """the cluster of the region you want to use"""

    attributes: object
    """Use this param to update the attributes of an asset in key:value format.

    Users can maintain any useful information or context about the assets by
    utilising this parameter.

    Please be careful when using this parameter while updating an asset as the new
    attributes object provided will completely overwrite the old attributes object.
    Use the _Update Asset Attributes_ method to add new or modify existing
    attributes.

    Another point to note is that the overall size of the attributes object cannot
    exceed 65kb and the maximum number of key:value pairs that can be added to this
    object is 100.
    """

    description: str
    """Use this param to update the description of an asset."""

    meta_data: MetaDataParam
    """Any valid json object data.

    Can be used to save customized data. Max size is 65kb.
    """

    name: str
    """Use this param to update the name of an asset.

    Users can assign meaningful custom names to their assets.
    """

    tags: List[str]
    """
    **This parameter will be deprecated soon! Please use the attributes parameter to
    add labels or markers for the asset.**

    Use this param to update the tags of an asset. tags can be used to filter asset
    in _Get Asset List_, **Search** and **Monitor** queries.
    """
