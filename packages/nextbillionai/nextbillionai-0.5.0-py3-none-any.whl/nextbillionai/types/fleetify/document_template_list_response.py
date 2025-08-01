# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .document_template_content_response import DocumentTemplateContentResponse

__all__ = ["DocumentTemplateListResponse", "Data"]


class Data(BaseModel):
    id: Optional[str] = None
    """Returns the unique ID of the document template."""

    content: Optional[List[DocumentTemplateContentResponse]] = None
    """
    An array of objects returning the details of data structures and validation
    rules and other properties of all document fields. Each object represents one
    document field.
    """

    name: Optional[str] = None
    """Returns the name of the document template."""


class DocumentTemplateListResponse(BaseModel):
    data: Optional[List[Data]] = None
    """
    An array of objects returning the details of each document template associated
    with the specified API key. Each object represents one document template. In
    case there are no templates associated with the given key, a blank array is
    returned.
    """

    msg: Optional[str] = None
    """Returns the error message in case of a failed request.

    If the request is successful, this field is not present in the response.
    """

    status: Optional[int] = None
    """Returns the HTTP response code."""
