# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .place_item_param import PlaceItemParam

__all__ = ["PlaceUpdateParams", "DataSource"]


class PlaceUpdateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    data_source: Annotated[DataSource, PropertyInfo(alias="dataSource")]
    """
    dataSource values can be updated to enhance or prioritize the search results to
    better suit specific business use cases.
    """

    place: Iterable[PlaceItemParam]
    """
    This parameter represents the place details, including geographical information,
    address and other related information.
    """

    score: int
    """Search score of the place.

    This is calculated based on how ‘richly’ the place is defined. For instance, a
    place with street name, city, state and country attributes set might be ranked
    lower than a place which has values of house, building, street name, city, state
    and country attributes set. The score determines the rank of the place among
    search results. You can also use this field to set a custom score as per its
    relevance to rank it among the search results from multiple data sources.
    """


class DataSource(TypedDict, total=False):
    ref_id: Annotated[str, PropertyInfo(alias="refId")]
    """
    This parameter represents the unique reference ID associated with the data
    source.
    """

    source: str
    """1.

    Move the place to a new dataset by setting the value to a unique dataset name.
    You can also move the place to an existing dataset by using an existing dataset
    name other than the current one. In both cases, the current datasource will be
    replaced for the specified docID.

    2. Update the place in an existing dataset by setting the name to the current
       value.
    """

    status: Literal["enable", "disable"]
    """
    Set this to either enable or disable to allow the place to be retrieved by a
    search API or block it respectively.
    """
