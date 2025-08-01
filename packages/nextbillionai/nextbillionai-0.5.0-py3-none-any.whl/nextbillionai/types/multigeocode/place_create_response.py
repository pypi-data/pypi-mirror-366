# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["PlaceCreateResponse"]


class PlaceCreateResponse(BaseModel):
    doc_id: Optional[str] = FieldInfo(alias="docId", default=None)
    """A unique NextBillion DocID will be created for the POI.

    Use this ID to search this place through the “Get Place” method, to update
    attributes or ‘status’ through the “Update Place” method or delete it using the
    “Delete Place” method.
    """
