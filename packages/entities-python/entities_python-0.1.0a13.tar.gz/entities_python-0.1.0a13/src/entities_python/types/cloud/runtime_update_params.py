# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["RuntimeUpdateParams"]


class RuntimeUpdateParams(TypedDict, total=False):
    identity: Required[str]

    max_turns: Required[int]
