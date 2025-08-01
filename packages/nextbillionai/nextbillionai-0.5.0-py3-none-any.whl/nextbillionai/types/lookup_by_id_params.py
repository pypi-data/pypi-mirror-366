# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["LookupByIDParams"]


class LookupByIDParams(TypedDict, total=False):
    id: Required[str]
    """
    Specify the unique identifier of a specific POI, Street, Geography, Point
    Address or other entities to retrieve its details.
    """

    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """
