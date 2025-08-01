# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .identity_param import IdentityParam
from ..toolbox.tool_param import ToolParam

__all__ = ["RuntimeUpdateParams"]


class RuntimeUpdateParams(TypedDict, total=False):
    identity: Required[IdentityParam]

    max_turns: Required[int]

    model: Required[str]

    tools: Required[Iterable[ToolParam]]
