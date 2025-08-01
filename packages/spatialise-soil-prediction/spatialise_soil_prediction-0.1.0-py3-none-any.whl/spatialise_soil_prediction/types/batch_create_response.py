# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from .._models import BaseModel
from .batch_status import BatchStatus

__all__ = ["BatchCreateResponse"]


class BatchCreateResponse(BaseModel):
    batch_id: str
    """Unique identifier for the batch"""

    created_at: datetime
    """Batch creation timestamp"""

    message: str
    """Human-readable status message"""

    status: BatchStatus
    """Current status of the batch"""

    total_jobs: int
    """Total number of jobs in the batch"""
