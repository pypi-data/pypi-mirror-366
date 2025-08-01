"""Serialization utilities for structured responses"""

import json
from pydantic import BaseModel


def default_json_serializer(obj: BaseModel) -> str:
    """Serializes a Pydantic model to a pretty JSON string."""
    return json.dumps(
        obj.model_dump(),
        ensure_ascii=False,
        indent=2,
    )