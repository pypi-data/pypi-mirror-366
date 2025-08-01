# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["SearchAroundParams"]


class SearchAroundParams(TypedDict, total=False):
    center: Required[str]
    """
    Location coordinates of the point which would act as the center of the circular
    area to be searched.
    """

    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    radius: Required[float]
    """Radius, in meters, of the circular area to be searched."""

    filter: str
    """
    **tags parameter will be deprecated soon! Please use the
    include_any_of_attributes or include_all_of_attributes parameters to match
    assets based on their labels or markers.**

    Use this parameter to filter the assets found inside the specified area by their
    tags. Multiple tags can be separated using commas (,).

    Please note the tags are case sensitive.
    """

    include_all_of_attributes: str
    """
    Use this parameter to filter the assets found inside the specified area by their
    attributes. Only the assets having all the attributes that are added to this
    parameter, will be returned in the search results. Multiple attributes can be
    separated using pipes (|).

    Please note the attributes are case sensitive. Also, this parameter can not be
    used in conjunction with include_any_of_attributes parameter.
    """

    include_any_of_attributes: str
    """
    Use this parameter to filter the assets found inside the specified area by their
    attributes. Assets having at least one of the attributes added to this
    parameter, will be returned in the search results. Multiple attributes can be
    separated using pipes (|).

    Please note the attributes are case sensitive. Also, this parameter can not be
    used in conjunction with include_all_of_attributes parameter.
    """

    max_search_limit: bool
    """
    When true, the maximum limit is 20Km for around search API and 48000 Km2 for
    other search methods.
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

    sort_by: Literal["distance", "duration", "straight_distance"]
    """Specify the metric to sort the assets returned in the search result.

    The valid values are:

    - **distance** : Sorts the assets by driving distance to the given
      sort_destination .
    - **duration** : Sorts the assets by travel time to the given sort_destination .
    - **straight_distance** : Sort the assets by straight-line distance to the given
      sort-destination .
    """

    sort_destination: str
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
