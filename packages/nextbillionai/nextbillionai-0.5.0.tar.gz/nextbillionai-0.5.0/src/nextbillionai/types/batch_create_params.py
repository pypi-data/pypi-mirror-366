# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

__all__ = ["BatchCreateParams", "Request"]


class BatchCreateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    requests: Iterable[Request]
    """
    An array of objects to collect the details of individual routing queries that
    will form a batch.
    """


class Request(TypedDict, total=False):
    query: str
    """Specify the routing query in the form of a string.

    The supported attributes and their formats are consistent with the standard
    routing endpoint that is being used as part of the batch. Check the
    [Sample Request](https://docs.nextbillion.ai/docs/navigation/batch-routing-api#sample-request-1)
    section for an example request.
    """
