"""Shared Pydantic base model.

CamelModel serializes to camelCase JSON (snake_case stays canonical in
Python) so the frontend never has to translate field names — see the
"API 契約不一致" pitfall in CLAUDE.md. All response schemas should extend
this instead of BaseModel directly.
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
