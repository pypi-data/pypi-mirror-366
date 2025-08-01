# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .document_template_content_response import DocumentTemplateContentResponse

__all__ = ["DocumentTemplateUpdateResponse", "Data"]


class Data(BaseModel):
    id: Optional[str] = None
    """Returns the unique ID of the document template."""

    content: Optional[List[DocumentTemplateContentResponse]] = None
    """
    An array of object returning the details of updated data structures and
    validation rules for document fields. Each object represents one document field.
    """

    name: Optional[str] = None
    """Returns the updated name of the document template."""


class DocumentTemplateUpdateResponse(BaseModel):
    data: Optional[Data] = None
    """An object returning the details of the updated document template."""

    msg: Optional[str] = None
    """Returns the error message in case of a failed request.

    If the request is successful, this field is not present in the response.
    """

    status: Optional[int] = None
    """Returns the HTTP response code."""
