# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["ContactObject", "Category"]


class Category(BaseModel):
    id: Optional[str] = None
    """Identifier number for an associated category. For example: "900-9300-0000" """


class ContactObject(BaseModel):
    categories: Optional[List[Category]] = None
    """The list of place categories this contact refers to."""

    label: Optional[str] = None
    """
    Optional label for the contact string, such as "Customer Service" or "Pharmacy
    Fax".
    """

    value: Optional[str] = None
    """Contact information, as specified by the contact type."""
