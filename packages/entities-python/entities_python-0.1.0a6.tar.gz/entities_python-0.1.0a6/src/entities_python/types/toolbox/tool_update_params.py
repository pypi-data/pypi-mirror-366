# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["ToolUpdateParams"]


class ToolUpdateParams(TypedDict, total=False):
    adapter: Optional[str]

    description: str

    name: str

    organization: Optional[str]

    parameters: object

    url: str
