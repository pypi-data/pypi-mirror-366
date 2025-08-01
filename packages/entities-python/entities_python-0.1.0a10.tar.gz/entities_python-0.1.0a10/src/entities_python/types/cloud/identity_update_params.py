# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["IdentityUpdateParams"]


class IdentityUpdateParams(TypedDict, total=False):
    memory: int

    name: str

    sleep_until: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]

    system_prompt: str

    timezone: str
