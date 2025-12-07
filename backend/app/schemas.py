# Pydantic response schemas for API
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from db.schema_types import ExitLink

class LocationOut(BaseModel):
    """Response schema for Location with JSON fields as real objects"""
    id: str
    name: str
    description: Optional[str] = None
    atmosphere: Optional[str] = None
    exits: List[ExitLink] = []
    immutable: bool = True
    
    class Config:
        from_attributes = True

class CharacterOut(BaseModel):
    """Response schema for Character with JSON fields as real objects"""
    id: str
    name: str
    bio: Optional[str] = None
    traits: Dict[str, Any] = {}
    last_known_location_id: Optional[str] = None
    immutable: bool = True
    
    class Config:
        from_attributes = True

class ItemOut(BaseModel):
    """Response schema for Item with JSON fields as real objects"""
    id: str
    name: str
    kind: Optional[str] = None
    seed_description: Optional[str] = None
    location_id: Optional[str] = None
    state: Dict[str, Any] = {}
    immutable: bool = True
    
    class Config:
        from_attributes = True


