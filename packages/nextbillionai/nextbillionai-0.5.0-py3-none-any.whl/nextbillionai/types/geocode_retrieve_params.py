# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["GeocodeRetrieveParams"]


class GeocodeRetrieveParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    q: Required[str]
    """Specify the free-text search query.

    Please note that whitespace, urls, email addresses, or other out-of-scope
    queries will yield no results.
    """

    at: str
    """Specify the center of the search context expressed as coordinates.

    Please note that one of "at", "in=circle" or "in=bbox" should be provided for
    relevant results.
    """

    in_: Annotated[str, PropertyInfo(alias="in")]
    """Search within a geographic area.

    This is a hard filter. Results will be returned if they are located within the
    specified area.

    A geographic area can be

    - a country (or multiple countries), provided as comma-separated
      [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country
      codes

      The country codes are to be provided in all uppercase.

      Format: countryCode:{countryCode}[,{countryCode}]

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

    lang: str
    """
    Select the language to be used for result rendering from a list of
    [BCP 47](https://en.wikipedia.org/wiki/IETF_language_tag) compliant language
    codes.
    """

    limit: int
    """Sets the maximum number of results to be returned."""
