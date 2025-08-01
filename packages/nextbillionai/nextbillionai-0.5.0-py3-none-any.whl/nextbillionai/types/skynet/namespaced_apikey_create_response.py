# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["NamespacedApikeyCreateResponse", "Result"]


class Result(BaseModel):
    apikey: Optional[str] = None
    """Returns the unique key created for the specified namespace."""

    created_at: Optional[int] = None
    """
    Returns the time, expressed as UNIX epoch timestamp in seconds, when the
    namespace key was created.
    """

    expires_at: Optional[int] = None
    """
    Returns the time, expressed as UNIX epoch timestamp in seconds, when the
    namespace key will expire.
    """

    namespace: Optional[str] = None
    """Returns the name of the namespace for which the key is created."""

    sub_id: Optional[str] = None
    """An internal subscription ID."""


class NamespacedApikeyCreateResponse(BaseModel):
    error: Optional[str] = None
    """Returns the error type in case of any error.

    If there is no error, then this field is absent in the response.
    """

    message: Optional[str] = None
    """Returns the error message in case of any error.

    If there is no error, then this field is absent in the response.
    """

    result: Optional[Result] = None
    """An object to return the details about the namespace key created."""

    status: Optional[int] = None
    """Returns the API response code."""
