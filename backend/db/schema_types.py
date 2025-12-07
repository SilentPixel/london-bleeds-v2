# Pydantic schema types for JSON columns
from pydantic import BaseModel
from typing import Dict, Union

class ExitLink(BaseModel):
    """Pydantic model for exit links in locations"""
    label: str
    to: str

# Type aliases for JSON column schemas
TraitMap = Dict[str, Union[bool, int, str]]
KVState = Dict[str, Union[bool, int, str]]
