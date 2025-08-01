# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .document_template_content_request_param import DocumentTemplateContentRequestParam

__all__ = ["DocumentTemplateCreateParams"]


class DocumentTemplateCreateParams(TypedDict, total=False):
    key: Required[str]
    """
    A key is a unique identifier that is required to authenticate a request to the
    API.
    """

    content: Required[Iterable[DocumentTemplateContentRequestParam]]
    """A form field that drivers must complete when executing a route step.

    Defines the data structure and validation rules for collecting required
    information during route execution.
    """

    name: Required[str]
    """Specify a name for the document template to be created."""
