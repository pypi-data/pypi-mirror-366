# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["Identity"]


class Identity(BaseModel):
    id: str

    created_at: datetime

    memory: int

    name: str

    organization: str

    sleep_until: Optional[datetime] = None

    system_prompt: Optional[str] = None

    timezone: Optional[str] = None
