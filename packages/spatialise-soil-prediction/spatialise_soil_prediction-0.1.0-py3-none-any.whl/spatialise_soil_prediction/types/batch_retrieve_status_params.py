# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["BatchRetrieveStatusParams"]


class BatchRetrieveStatusParams(TypedDict, total=False):
    cursor: str
    """Pagination cursor from previous response to fetch next page"""

    limit: int
    """Maximum number of jobs to return per page"""
