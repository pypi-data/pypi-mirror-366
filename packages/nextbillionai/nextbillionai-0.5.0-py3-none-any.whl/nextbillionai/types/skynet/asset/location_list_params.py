# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["LocationListParams"]


class LocationListParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    cluster: Literal["america"]
    """the cluster of the region you want to use"""

    correction: str
    """Describe the geometry characteristics through a , separated list of properties.

    Setting mapmatch to 1 returns the geometry of the tracked points, snapped to the
    nearest road.

    Setting interpolate to 1 smoothens the snapped geometry by adding more points,
    as needed. Please note, mapmatch should be set to 1 for interpolate to be
    effective.

    mode is used to set the transport mode for which the snapped route will be
    determined. Allowed values for mode are car and truck.
    """

    end_time: int
    """Time until which the tracked locations of the asset need to be retrieved."""

    geometry_type: Literal["polyline", "polyline6", "geojson"]
    """
    Set the geometry format to encode the path linking the tracked locations of the
    asset.

    Please note that geometry_type is effective only when mapmatch property of
    correction parameter is set to 1.
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

    start_time: int
    """Time after which the tracked locations of the asset need to be retrieved."""
