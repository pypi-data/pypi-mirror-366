# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from ..geofence_entity_create_param import GeofenceEntityCreateParam

__all__ = ["BatchCreateParams"]


class BatchCreateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    geofences: Iterable[GeofenceEntityCreateParam]
    """
    An array of objects to collect the details of the multiple geofences that need
    to be created.
    """
