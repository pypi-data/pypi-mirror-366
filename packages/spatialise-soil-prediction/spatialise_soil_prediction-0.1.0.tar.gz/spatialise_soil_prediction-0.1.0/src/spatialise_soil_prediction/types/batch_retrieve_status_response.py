# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .batch_status import BatchStatus

__all__ = ["BatchRetrieveStatusResponse", "Job"]


class Job(BaseModel):
    created_at: datetime

    job_id: str

    status: Literal["pending", "running", "completed", "failed", "cancelled"]
    """Status of an individual job."""

    updated_at: datetime

    error_message: Optional[str] = None
    """Error message if job failed"""

    result_url: Optional[str] = None
    """Temporary signed URL to download result GeoTIFF. Valid for 6 hours."""


class BatchRetrieveStatusResponse(BaseModel):
    batch_id: str
    """Unique identifier for the batch"""

    completed_jobs: int

    created_at: datetime

    failed_jobs: int

    has_more: bool
    """Whether there are more jobs to fetch"""

    jobs: List[Job]
    """Status of individual jobs in this page"""

    next_cursor: Optional[str] = None
    """Cursor for fetching the next page. Null if no more pages."""

    pending_jobs: int

    status: BatchStatus
    """Current status of the batch"""

    total_jobs: int

    updated_at: datetime
