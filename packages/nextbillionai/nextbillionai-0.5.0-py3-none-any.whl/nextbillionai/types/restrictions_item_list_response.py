# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel

__all__ = [
    "RestrictionsItemListResponse",
    "RestrictionsItemListResponseItem",
    "RestrictionsItemListResponseItemCoordinate",
]


class RestrictionsItemListResponseItemCoordinate(BaseModel):
    lat: Optional[float] = None

    lon: Optional[float] = None


class RestrictionsItemListResponseItem(BaseModel):
    id: float

    area: str

    coordinate: RestrictionsItemListResponseItemCoordinate

    group_id: float

    group_type: Literal["segment", "turn"]

    mode: List[Literal["0w", "1w", "2w", "3w", "4w", "6w"]]

    repeat_on: str

    restriction_type: Literal["closure", "fixedspeed", "maxspeed", "turn", "truck"]

    source: Literal["rrt", "pbf"]

    state: Literal["enabled", "disabled", "deleted"]

    status: Literal["active", "inactive"]


RestrictionsItemListResponse: TypeAlias = List[RestrictionsItemListResponseItem]
