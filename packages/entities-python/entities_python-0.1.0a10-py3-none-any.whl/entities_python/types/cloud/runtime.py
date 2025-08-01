# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime

from .identity import Identity
from ..._models import BaseModel
from .status_enum import StatusEnum
from ..toolbox.tool import Tool

__all__ = ["Runtime"]


class Runtime(BaseModel):
    id: str

    created_at: datetime

    current_turn: int

    identity: Identity

    max_turns: int

    model: str

    status: StatusEnum
    """
    - `created` - Created
    - `pending` - Pending
    - `running` - Running
    - `completed` - Completed
    - `failed` - Failed
    """

    tools: List[Tool]
