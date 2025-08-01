# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["NamespacedApikeyCreateParams"]


class NamespacedApikeyCreateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    namespace: Required[str]
    """Specify a name for the namespace.

    If the namespace specified is unique then a new namespace along with a new key
    is created. Whereas if the specified namespace is not unique, a new key will be
    created in the existing namespace. Please note that a namespace cannot be
    created using another namespace key.
    """
