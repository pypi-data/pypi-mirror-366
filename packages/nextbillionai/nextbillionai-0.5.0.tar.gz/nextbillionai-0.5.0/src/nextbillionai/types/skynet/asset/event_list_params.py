# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["EventListParams"]


class EventListParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    cluster: Literal["america"]
    """the cluster of the region you want to use"""

    end_time: int
    """Time before which the events triggered by the asset need to be retrieved."""

    monitor_id: str
    """Filter the events by monitor_id.

    When provided, only the events triggered by the monitor will be returned in
    response.

    Please note that if the attributes of the asset identified by id and those of
    the monitor do not match, then no events might be returned for this monitor_id.
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
    """Time after which the events triggered by the asset need to be retrieved."""
