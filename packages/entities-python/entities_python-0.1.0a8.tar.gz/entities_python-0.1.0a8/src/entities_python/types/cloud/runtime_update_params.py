# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["RuntimeUpdateParams"]


class RuntimeUpdateParams(TypedDict, total=False):
    agent_key: str

    current_turn: int

    max_turns: int

    memory: int

    model: str

    status: Literal["pending", "running", "completed", "failed"]
    """
    - `pending` - Pending
    - `running` - Running
    - `completed` - Completed
    - `failed` - Failed
    """

    tools: List[str]
