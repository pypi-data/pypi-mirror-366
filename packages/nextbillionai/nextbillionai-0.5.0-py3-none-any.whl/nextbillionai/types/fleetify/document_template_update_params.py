# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .document_template_content_request_param import DocumentTemplateContentRequestParam

__all__ = ["DocumentTemplateUpdateParams"]


class DocumentTemplateUpdateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    content: Iterable[DocumentTemplateContentRequestParam]
    """
    An object to collect the details of form fields to be updated - data structures,
    validation rules. Please note that the details provided here will overwrite any
    existing document fields in the given template.
    """

    name: str
    """Specify the document template name to be updated."""
