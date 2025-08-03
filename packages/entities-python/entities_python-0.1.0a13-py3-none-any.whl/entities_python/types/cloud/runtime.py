# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from ..._models import BaseModel
from .status_enum import StatusEnum

__all__ = ["Runtime"]


class Runtime(BaseModel):
    id: str

    created_at: datetime

    current_turn: int

    identity: str

    max_turns: int

    status: StatusEnum
    """
    - `created` - Created
    - `pending` - Pending
    - `running` - Running
    - `completed` - Completed
    - `failed` - Failed
    """
