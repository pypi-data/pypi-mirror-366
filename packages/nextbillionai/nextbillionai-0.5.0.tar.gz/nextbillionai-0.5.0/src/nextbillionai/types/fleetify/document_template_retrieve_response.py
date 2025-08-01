# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .document_template_content_response import DocumentTemplateContentResponse

__all__ = ["DocumentTemplateRetrieveResponse", "Data"]


class Data(BaseModel):
    id: Optional[str] = None
    """Returns the unique identifier of the document template."""

    content: Optional[List[DocumentTemplateContentResponse]] = None
    """
    An array of objects returning the details of data structures and validation
    rules and other properties of all document fields. Each object represents one
    document field.
    """

    name: Optional[str] = None
    """
    Returns the name of the document template as specified at the time of creating
    the template.
    """


class DocumentTemplateRetrieveResponse(BaseModel):
    data: Optional[Data] = None
    """An object returning the details of the requested document template."""

    msg: Optional[str] = None
    """Returns the error message in case of a failed request.

    If the request is successful, this field is not present in the response.
    """

    status: Optional[int] = None
    """Returns the HTTP response code."""
