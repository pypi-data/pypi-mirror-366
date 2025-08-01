# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["Categories"]


class Categories(BaseModel):
    id: Optional[str] = None
    """Identifier number for an associated category."""

    name: Optional[str] = None
    """Name of the place category in the result item language."""

    primary: Optional[str] = None
    """Whether or not it is a primary category.

    This field is visible only when the value is 'true'.
    """
