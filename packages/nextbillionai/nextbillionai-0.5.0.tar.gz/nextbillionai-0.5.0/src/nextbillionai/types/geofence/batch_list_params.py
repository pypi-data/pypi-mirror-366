# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["BatchListParams"]


class BatchListParams(TypedDict, total=False):
    ids: Required[str]
    """Comma(,) separated list of IDs of the geofences to be searched."""

    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """
