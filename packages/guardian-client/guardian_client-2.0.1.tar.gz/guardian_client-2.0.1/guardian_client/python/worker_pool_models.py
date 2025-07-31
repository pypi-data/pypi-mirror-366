from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class WorkerPoolStatus(str, Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class WorkerPoolHealth(str, Enum):
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


class WorkerPoolResponse(BaseModel):
    """Response model for worker pool operations."""

    keycloak_client_id: str = Field(
        ..., description="Keycloak Client ID of the worker pool"
    )
    name: Optional[str] = Field(None, description="Name of the worker pool")
    description: Optional[str] = Field(
        None, description="Optional description for the worker pool"
    )
    status: WorkerPoolStatus = Field(
        ..., description="Current status of the worker pool (ENABLED/DISABLED)"
    )
    health: WorkerPoolHealth = Field(
        ..., description="Current health status of the worker pool"
    )
    last_heartbeat_at: Optional[datetime] = Field(
        None, description="Timestamp of the last heartbeat"
    )
    last_sync: Optional[datetime] = Field(
        None, description="Timestamp of the last sync"
    )
    created_at: datetime = Field(
        ..., description="Timestamp when the worker pool was created"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the worker pool was last updated"
    )


class WorkerPoolListResponse(BaseModel):
    """Response model for listing worker pools."""

    worker_pools: List[WorkerPoolResponse] = Field(
        ..., description="List of worker pools"
    )
    pagination: dict = Field(..., description="Pagination information with total_items")


class WorkerPoolUpdateRequest(BaseModel):
    """Request model for updating worker pool metadata or status."""

    name: Optional[str] = Field(
        None, description="New friendly name for the worker pool"
    )
    description: Optional[str] = Field(
        None, description="New description for the worker pool"
    )
    status: Optional[WorkerPoolStatus] = Field(
        None, description="New status for the worker pool"
    )
