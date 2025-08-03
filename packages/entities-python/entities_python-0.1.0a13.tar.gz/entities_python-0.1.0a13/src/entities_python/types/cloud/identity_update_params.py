# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["IdentityUpdateParams"]


class IdentityUpdateParams(TypedDict, total=False):
    locked_at: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]

    memory: int

    model: str

    name: str

    sleep_until: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]

    system_prompt: str

    timezone: str

    tools: List[str]
