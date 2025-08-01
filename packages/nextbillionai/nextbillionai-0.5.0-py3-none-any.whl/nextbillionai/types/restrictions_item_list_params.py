# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RestrictionsItemListParams"]


class RestrictionsItemListParams(TypedDict, total=False):
    max_lat: Required[float]

    max_lon: Required[float]

    min_lat: Required[float]

    min_lon: Required[float]

    group_id: float

    mode: Literal["0w", "1w", "2w", "3w", "4w", "6w"]

    restriction_type: Literal["turn", "parking", "fixedspeed", "maxspeed", "closure", "truck"]

    source: str

    state: Literal["enabled", "disabled", "deleted"]

    status: Literal["active", "inactive"]
