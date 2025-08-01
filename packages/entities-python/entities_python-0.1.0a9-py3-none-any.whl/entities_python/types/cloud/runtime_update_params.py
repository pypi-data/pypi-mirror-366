# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from ..toolbox.tool_param import ToolParam

__all__ = ["RuntimeUpdateParams", "Identity"]


class RuntimeUpdateParams(TypedDict, total=False):
    identity: Identity

    max_turns: int

    model: str

    tools: Iterable[ToolParam]


class Identity(TypedDict, total=False):
    memory: Required[int]

    name: Required[str]

    sleep_until: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]

    system_prompt: str

    timezone: str
