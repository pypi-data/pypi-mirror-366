# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

__all__ = ["GeocodeBatchCreateParams", "Body"]


class GeocodeBatchCreateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    body: Required[Iterable[Body]]


_BodyReservedKeywords = TypedDict(
    "_BodyReservedKeywords",
    {
        "in": str,
    },
    total=False,
)


class Body(_BodyReservedKeywords, total=False):
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

    lang: str
    """
    Select the language to be used for result rendering from a list of
    [BCP 47](https://en.wikipedia.org/wiki/IETF_language_tag) compliant language
    codes.
    """

    limit: int
    """Maximum number of results to be returned.

    Please note that the minimum value that can be provided is 1 and the maximum
    that can be provided is 100.
    """
