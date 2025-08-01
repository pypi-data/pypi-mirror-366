# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from ..toolbox.tool import Tool

__all__ = ["RuntimeListResponse", "RuntimeListResponseItem", "RuntimeListResponseItemIdentity"]


class RuntimeListResponseItemIdentity(BaseModel):
    id: str

    created_at: datetime

    memory: int

    name: str

    organization: str

    sleep_until: Optional[datetime] = None

    system_prompt: Optional[str] = None

    timezone: Optional[str] = None


class RuntimeListResponseItem(BaseModel):
    id: str

    created_at: datetime

    current_turn: int

    identity: RuntimeListResponseItemIdentity

    max_turns: int

    model: str

    status: Literal["created", "pending", "running", "completed", "failed"]
    """
    - `created` - Created
    - `pending` - Pending
    - `running` - Running
    - `completed` - Completed
    - `failed` - Failed
    """

    tools: List[Tool]


RuntimeListResponse: TypeAlias = List[RuntimeListResponseItem]
