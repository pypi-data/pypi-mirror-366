# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["TripEndParams"]


class TripEndParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    id: Required[str]
    """Specify the ID of the trip to be ended."""

    cluster: Literal["america"]
    """the cluster of the region you want to use"""
