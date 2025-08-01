# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["GeofenceListParams"]


class GeofenceListParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
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

    tags: str
    """Comma (,) separated list of tags which will be used to filter the geofences.

    Please note only the geofences which have all the tags added to this parameter
    will be included in the result. This parameter can accept a string with a
    maximum length of 256 characters.
    """
