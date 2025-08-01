from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FileData(BaseModel):
    path: str
    content: Optional[str] = None
    version: int
    created_at: datetime
    updated_at: datetime