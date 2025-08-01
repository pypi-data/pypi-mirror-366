# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .pagination import Pagination
from .asset.track_location import TrackLocation

__all__ = ["SearchResponse", "Data", "DataAsset", "DataAssetRankingInfo"]


class DataAssetRankingInfo(BaseModel):
    distance: Optional[float] = None
    """Driving distance between the asset and the sort_destination."""

    duration: Optional[float] = None
    """Driving duration between the asset and the sort_destination.

    Please note this field in not returned in the response when sort_by =
    straight_distance .
    """

    index: Optional[int] = None
    """Index of the ranked asset. The index value starts from 0."""


class DataAsset(BaseModel):
    id: Optional[str] = None
    """
    ID of asset which was last located inside the specified area in the input
    request. This is the same ID that was generated/provided at the time of creating
    the asset.
    """

    created_at: Optional[int] = None
    """
    A UNIX timestamp in seconds representing the time at which the asset was
    created.
    """

    description: Optional[str] = None
    """Description of the asset.

    The value would be the same as that provided for the description parameter at
    the time of creating or updating the asset.
    """

    latest_location: Optional[TrackLocation] = None
    """An object with details of the tracked location.

    Please note that if there are no tracking records for an asset, no location data
    will be returned.
    """

    meta_data: Optional[object] = None
    """Any valid json object data.

    Can be used to save customized data. Max size is 65kb.
    """

    name: Optional[str] = None
    """Name of asset.

    The value would be the same as that provided for the name parameter at the time
    of creating or updating the asset.
    """

    ranking_info: Optional[DataAssetRankingInfo] = None
    """
    An object returning the sorting details of the asset as per the configuration
    specified in the input.
    """

    tags: Optional[List[str]] = None
    """
    **This parameter will be deprecated soon! Please move existing tags to
    attributes parameter.**

    Tags associated with the asset.
    """

    tracked_at: Optional[int] = None
    """
    A UNIX epoch timestamp in seconds representing the last time when the asset was
    tracked.
    """

    updated_at: Optional[int] = None
    """
    A UNIX timestamp in seconds representing the time at which the asset was last
    updated.
    """


class Data(BaseModel):
    assets: Optional[List[DataAsset]] = None
    """An array of objects with details of the asset(s) returned in the search result.

    Each object represents one asset
    """

    page: Optional[Pagination] = None
    """An object with pagination details of the search results.

    Use this object to implement pagination in your application.
    """


class SearchResponse(BaseModel):
    data: Optional[Data] = None
    """A data object containing the search result."""

    message: Optional[str] = None
    """Displays the error message in case of a failed request.

    If the request is successful, this field is not present in the response.
    """

    status: Optional[str] = None
    """A string indicating the state of the response.

    On successful responses, the value will be Ok. Indicative error messages are
    returned for different errors. See the [API Error Codes](#api-error-codes)
    section below for more information.
    """
