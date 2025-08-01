# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["GeocodeStructuredRetrieveParams"]


class GeocodeStructuredRetrieveParams(TypedDict, total=False):
    country_code: Required[Annotated[str, PropertyInfo(alias="countryCode")]]
    """
    Specify a valid
    [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country
    code in which the place being searched should be located. Please note that this
    is a case-sensitive field and the country code should be in all uppercase.
    """

    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    at: str
    """Specify the center of the search context expressed as coordinates.

    Please note that one of "at", "in=circle" or "in=bbox" should be provided for
    relevant results.
    """

    city: str
    """Specify the city in which the place being searched should be located."""

    county: str
    """
    Specify the county division of the state in which the place being searched
    should be located.
    """

    house_number: Annotated[str, PropertyInfo(alias="houseNumber")]
    """Specify the house number of the place being searched."""

    in_: Annotated[str, PropertyInfo(alias="in")]
    """Search within a geographic area.

    This is a hard filter. Results will be returned if they are located within the
    specified area.

    A geographic area can be

    - a circular area, provided as latitude, longitude, and radius (an integer with
      meters as unit)

      Format: circle:{latitude},{longitude};r={radius}

    - a bounding box, provided as _west longitude_, _south latitude_, _east
      longitude_, _north latitude_

      Format: bbox:{west longitude},{south latitude},{east longitude},{north
      latitude}

    Please provide one of 'at', 'in=circle' or 'in=bbox' input for a relevant
    result.
    """

    limit: int
    """Sets the maximum number of results to be returned."""

    postal_code: Annotated[str, PropertyInfo(alias="postalCode")]
    """Specify the postal code in which the place being searched should be located."""

    state: str
    """
    Specify the state division of the country in which the place being searched
    should be located.
    """

    street: str
    """
    Specify the name of the street in which the place being searched should be
    located.
    """
