# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

from .meta_data_param import MetaDataParam

__all__ = ["AssetCreateParams"]


class AssetCreateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    cluster: Literal["america"]
    """the cluster of the region you want to use"""

    attributes: object
    """
    attributes can be used to store custom information about an asset in key:value
    format. Use attributes to add any useful information or context to your assets
    like the vehicle type, shift timing etc. Moreover, these attributes can be used
    to filter assets in **Search**, **Monitor**, and _Get Asset List_ queries.

    Please note that the maximum number of key:value pairs that can be added to an
    attributes object is 100. Also, the overall size of attributes object should not
    exceed 65kb.
    """

    custom_id: str
    """Set a unique ID for the new asset.

    If not provided, an ID will be automatically generated in UUID format. A valid
    custom*id can contain letters, numbers, "-", & "*" only.

    Please note that the ID of an asset can not be changed once it is created.
    """

    description: str
    """Description for the asset."""

    meta_data: MetaDataParam
    """Any valid json object data.

    Can be used to save customized data. Max size is 65kb.
    """

    name: str
    """Name of the asset.

    Use this field to assign a meaningful, custom name to the asset being created.
    """

    tags: List[str]
    """
    **This parameter will be deprecated soon! Please use the attributes parameter to
    add labels or markers for the asset.**

    Tags of the asset. tags can be used for filtering assets in operations like _Get
    Asset List_ and asset **Search** methods. They can also be used for monitoring
    of assets using the **Monitor** methods after linking tags and asset.

    Valid tags are strings consisting of alphanumeric characters (A-Z, a-z, 0-9)
    along with the underscore ('\\__') and hyphen ('-') symbols.
    """
