from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"

class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    created_at: Optional[datetime] = None

class TaskResult(BaseModel):
    task_id: str
    status: TaskStatus
    file_url: Optional[str] = None
    error: Optional[str] = None
    progress: Optional[float] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None