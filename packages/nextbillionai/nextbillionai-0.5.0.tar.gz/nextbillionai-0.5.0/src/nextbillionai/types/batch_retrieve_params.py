# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["BatchRetrieveParams"]


class BatchRetrieveParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    track_id: Required[str]
    """
    Specify the track ID of the batch that was returned in the response after
    submitting a successful batch request.
    """
