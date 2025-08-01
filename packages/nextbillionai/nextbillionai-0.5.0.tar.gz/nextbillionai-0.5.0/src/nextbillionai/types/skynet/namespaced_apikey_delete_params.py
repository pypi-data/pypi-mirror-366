# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["NamespacedApikeyDeleteParams"]


class NamespacedApikeyDeleteParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API. Please note for the delete namespace key operation another namespace key
    cannot be used.

    The namespace created using this key can be managed using the APIs & Services >
    Credentials section of user’s
    [NextBillion Console](https://console.nextbillion.ai).
    """

    key_to_delete: Required[str]
    """Specify the key to be deleted."""

    namespace: Required[str]
    """Specify the name of the namespace to which the \\kkey_to_delete\\  belongs.

    Please note that a namespace key cannot be deleted using another namespace key.
    """
