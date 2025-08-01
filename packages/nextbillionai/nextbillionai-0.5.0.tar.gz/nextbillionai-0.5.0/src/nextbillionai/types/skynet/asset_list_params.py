# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["AssetListParams"]


class AssetListParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    cluster: Literal["america"]
    """the cluster of the region you want to use"""

    include_all_of_attributes: str
    """Use this parameter to filter the assets by their attributes.

    Only the assets having all the attributes added to this parameter, will be
    returned in the response. Multiple attributes can be separated using pipes (|).

    Please note the attributes are case sensitive. Also, this parameter can not be
    used in conjunction with include_any_of_attributes parameter.
    """

    include_any_of_attributes: str
    """Use this parameter to filter the assets by their attributes.

    Assets having at least one of the attributes added to this parameter, will be
    returned in the response. Multiple attributes can be separated using pipes (|).

    Please note the attributes are case sensitive. Also, this parameter can not be
    used in conjunction with include_all_of_attributes parameter.
    """

    pn: int
    """Denotes page number.

    Use this along with the ps parameter to implement pagination for your searched
    results. This parameter does not have a maximum limit but would return an empty
    response in case a higher value is provided when the result-set itself is
    smaller.
    """

    ps: int
    """Denotes number of search results per page.

    Use this along with the pn parameter to implement pagination for your searched
    results.
    """

    sort: str
    """Provide a single field to sort the results by.

    Only updated_at or created_at fields can be selected for ordering the results.

    By default, the result is sorted by created_at field in the descending order.
    Allowed values for specifying the order are asc for ascending order and desc for
    descending order.
    """

    tags: str
    """
    **This parameter will be deprecated soon! Please use the
    include_all_of_attributes or include_any_of_attributes parameters to provide
    labels or markers for the assets to be retrieved.**

    tags can be used to filter the assets. Only those assets which have all the tags
    provided, will be included in the result. In case multiple tags need to be
    specified, use , to separate them.
    """
