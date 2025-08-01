# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["Tool"]


class Tool(BaseModel):
    id: str

    description: str

    name: str

    parameters: object

    url: str

    adapter: Optional[str] = None

    organization: Optional[str] = None
