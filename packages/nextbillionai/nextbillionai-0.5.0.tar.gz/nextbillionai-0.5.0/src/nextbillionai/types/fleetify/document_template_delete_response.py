# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["DocumentTemplateDeleteResponse"]


class DocumentTemplateDeleteResponse(BaseModel):
    msg: Optional[str] = None
    """Returns the error message in case of a failed request.

    If the request is successful, this field is not present in the response.
    """

    status: Optional[int] = None
    """Returns the HTTP response code."""
