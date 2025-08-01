# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RestrictionListParams"]


class RestrictionListParams(TypedDict, total=False):
    area: Required[str]
    """Specify the area name. It represents a region where restrictions can be applied.

    _The area it belongs to. See Area API_
    """

    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    limit: Required[int]
    """The number of restrictions to be returned in the response.

    Please note that if the limit is set to a number more than the total number of
    available restrictions, then all restrictions would be returned together.
    """

    offset: Required[int]
    """
    An integer value indicating the number of items in the collection that need to
    be skipped in the response. Please note that the offset starts from 0, so the
    first item returned in the result would be the item at (offset + 1) position in
    collection.

    Users can use offset along with limit to implement paginated result.
    """

    mode: Literal["0w", "2w", "3w", "4w", "6w"]
    """Specify the modes of travel that the restriction pertains to."""

    name: str
    """The name of the restriction.

    This should be same as that provided while creating or updating the restriction.
    """

    restriction_type: Literal["turn", "parking", "fixedspeed", "maxspeed", "closure", "truck"]
    """Specify the type of restrictions to fetch."""

    source: Literal["rrt", "pbf"]
    """
    It represents where it comes from, currently the possible values include "rrt",
    "xsm"
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
    """a internal parameter"""
