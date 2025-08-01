# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["PolygonCreateParams", "Polygon", "MatchFilter", "Sort", "SortSortDestination"]


class PolygonCreateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    polygon: Required[Polygon]
    """An object to collect geoJSON details of a custom polygon. Please ensure that:

    - the polygon provided is enclosed. This can be achieved by making the last
      location coordinate in the list equal to the first location coordinate of the
      list.

    - the 'polygon' provided does not contain multiple rings.

    The contents of this object follow the
    [geoJSON standard](https://datatracker.ietf.org/doc/html/rfc7946).

    Please note that the maximum area of the search polygon allowed is 3000
    km<sup>2</sup>.
    """

    filter: str
    """
    **tags parameter will be deprecated soon! Please use the
    include_any_of_attributes or include_all_of_attributes parameters to match
    assets based on their labels or markers.**

    Use this parameter to filter the assets found inside the specified area by their
    tag. Multiple tag can be separated using comma (,).

    Please note the tags are case sensitive.
    """

    match_filter: MatchFilter
    """
    An object to define the attributes which will be used to filter the assets found
    within the polygon.
    """

    max_search_limit: bool
    """if ture, can get 16x bigger limitation in search."""

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
    results. Please note that ps has a default value of 20 and accepts integers only
    in the range of [1, 100].
    """

    sort: Sort


class Polygon(TypedDict, total=False):
    coordinates: Required[Iterable[float]]
    """
    An array of coordinates in the [longitude, latitude] format, representing the
    polygon boundary.
    """

    type: Required[str]
    """Type of the geoJSON geometry. Should always be polygon."""


class MatchFilter(TypedDict, total=False):
    include_all_of_attributes: str
    """
    Use this parameter to filter the assets found inside the specified area by their
    attributes. Only the assets having all the attributes that are added to this
    parameter, will be returned in the search results. Multiple attributes can be
    separated using commas (,).

    Please note the attributes are case sensitive. Also, this parameter can not be
    used in conjunction with include_any_of_attributes parameter.
    """

    include_any_of_attributes: str
    """
    Use this parameter to filter the assets found inside the specified area by their
    attributes. Assets having at least one of the attributes added to this
    parameter, will be returned in the search results. Multiple attributes can be
    separated using commas (,).

    Please note the attributes are case sensitive. Also, this parameter can not be
    used in conjunction with include_all_of_attributes parameter.
    """


class SortSortDestination(TypedDict, total=False):
    lat: Required[float]
    """Latitude of the destination location"""

    lon: Required[float]
    """Longitude of the destination location"""


class Sort(TypedDict, total=False):
    sort_by: Literal["distance", "duration", "straight_distance"]
    """Specify the metric to sort the assets returned in the search result.

    The valid values are:

    - **distance** : Sorts the assets by driving distance to the given
      sort_destination .
    - **duration** : Sorts the assets by travel time to the given sort_destination .
    - **straight_distance** : Sort the assets by straight-line distance to the given
      sort-destination .
    """

    sort_destination: SortSortDestination
    """
    Specifies the location coordinates of the point which acts as destination for
    sorting the assets in the search results. The service will sort each asset based
    on the driving distance or travel time to this destination, from its current
    location. Use the sort_by parameter to configure the metric that should be used
    for sorting the assets. Please note that sort_destination is required when
    sort_by is provided.
    """

    sort_driving_mode: Literal["car", "truck"]
    """
    Specifies the driving mode to be used for determining travel duration or driving
    distance for sorting the assets in search result.
    """
