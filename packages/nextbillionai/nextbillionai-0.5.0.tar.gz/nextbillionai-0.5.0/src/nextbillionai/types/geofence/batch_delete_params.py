# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

__all__ = ["BatchDeleteParams"]


class BatchDeleteParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    ids: List[str]
    """An array IDs of the geofence to be deleted.

    These are the IDs that were generated/provided at the time of creating the
    respective geofences.
    """
