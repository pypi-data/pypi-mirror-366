# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

__all__ = ["RuntimeCreateParams"]


class RuntimeCreateParams(TypedDict, total=False):
    agent_key: Required[str]

    current_turn: Required[int]

    max_turns: Required[int]

    memory: Required[int]

    model: Required[str]

    status: Literal["pending", "running", "completed", "failed"]
    """
    - `pending` - Pending
    - `running` - Running
    - `completed` - Completed
    - `failed` - Failed
    """

    tools: List[str]
