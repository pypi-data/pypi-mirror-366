# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .contact_object import ContactObject

__all__ = ["Contacts"]


class Contacts(BaseModel):
    email: Optional[List[ContactObject]] = None

    fax: Optional[List[ContactObject]] = None

    mobile: Optional[List[ContactObject]] = None

    phone: Optional[List[ContactObject]] = None

    toll_free: Optional[List[ContactObject]] = FieldInfo(alias="tollFree", default=None)

    www: Optional[List[ContactObject]] = None
