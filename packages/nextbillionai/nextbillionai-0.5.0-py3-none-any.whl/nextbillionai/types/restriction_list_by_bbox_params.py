# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

__all__ = ["RestrictionListByBboxParams"]


class RestrictionListByBboxParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    max_lat: Required[float]
    """Specifies the maximum latitude value for the bounding box."""

    max_lon: Required[float]
    """Specifies the maximum longitude value for the bounding box."""

    min_lat: Required[float]
    """Specifies the minimum latitude value for the bounding box."""

    min_lon: Required[float]
    """Specifies the minimum longitude value for the bounding box."""

    mode: List[Literal["0w", "2w", "3w", "4w", "6w"]]
    """Specify the modes of travel that the restriction pertains to."""

    restriction_type: Literal["turn", "parking", "fixedspeed", "maxspeed", "closure", "truck"]
    """Specify the type of restrictions to fetch."""

    source: Literal["rrt", "pbf"]
    """
    This parameter represents where the restriction comes from and cannot be
    modified by clients sending requests to the API endpoint.

    For example, an API endpoint that returns a list of restrictions could include
    the source parameter to indicate where each item comes from. This parameter can
    be useful for filtering, sorting, or grouping the results based on their source.
    """

    state: Literal["enabled", "disabled", "deleted"]
    """This parameter is used to filter restrictions based on their state i.e.

    whether the restriction is currently enabled, disabled, or deleted. For example,
    users can retrieve a list of all the deleted restrictions by setting
    state=deleted.
    """

    status: Literal["active", "inactive"]
    """Restrictions can be active or inactive at a given time by virtue of their
    nature.

    For example, maximum speed limits can be active on the roads leading to schools
    during school hours and be inactive afterwards or certain road closure
    restrictions be active during holidays/concerts and be inactive otherwise.

    Use this parameter to filter the restrictions based on their status at the time
    of making the request i.e. whether they are in force or not.
    """

    transform: bool
    """This is internal parameter with a default value as false."""
