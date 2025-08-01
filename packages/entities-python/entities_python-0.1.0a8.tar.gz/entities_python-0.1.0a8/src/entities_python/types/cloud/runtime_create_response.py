# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RuntimeCreateResponse"]


class RuntimeCreateResponse(BaseModel):
    id: str

    agent_key: str

    created_at: datetime

    current_turn: int

    max_turns: int

    memory: int

    model: str

    organization: str

    status: Optional[Literal["pending", "running", "completed", "failed"]] = None
    """
    - `pending` - Pending
    - `running` - Running
    - `completed` - Completed
    - `failed` - Failed
    """

    tools: Optional[List[str]] = None
