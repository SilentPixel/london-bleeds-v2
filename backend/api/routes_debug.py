# Debug routes for development
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from db.engine import get_db
from db.models import Location, Character, Item
from app.schemas import LocationOut, CharacterOut, ItemOut
from db.saves import create_save_slot, get_save_slots
from db.seed import upsert_location

router = APIRouter()

class SaveSlotRequest(BaseModel):
    name: str

class SaveSlotResponse(BaseModel):
    id: str
    player_id: str
    name: str
    created_at: str

@router.get("/locations", response_model=List[LocationOut])
async def debug_locations(db: Session = Depends(get_db)):
    """List all locations"""
    locations = db.query(Location).all()
    return [LocationOut.model_validate(location.to_dict()) for location in locations]

@router.get("/characters", response_model=List[CharacterOut])
async def debug_characters(db: Session = Depends(get_db)):
    """List all characters"""
    characters = db.query(Character).all()
    return [CharacterOut.model_validate(character.to_dict()) for character in characters]

@router.get("/items", response_model=List[ItemOut])
async def debug_items(db: Session = Depends(get_db)):
    """List all items"""
    items = db.query(Item).all()
    return [ItemOut.model_validate(item.to_dict()) for item in items]

@router.post("/save/{player_id}", response_model=SaveSlotResponse)
async def create_save(player_id: str, request: SaveSlotRequest, db: Session = Depends(get_db)):
    """Create a named save slot for a player"""
    try:
        save_slot = create_save_slot(db, player_id, request.name)
        return SaveSlotResponse(
            id=save_slot.id,
            player_id=save_slot.player_id,
            name=save_slot.name,
            created_at=save_slot.created_at.isoformat() if save_slot.created_at else ""
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/save/{player_id}", response_model=List[Dict[str, Any]])
async def list_saves(player_id: str, db: Session = Depends(get_db)):
    """List all save slots for a player"""
    save_slots = get_save_slots(db, player_id)
    return [
        {
            "id": slot.id,
            "player_id": slot.player_id,
            "name": slot.name,
            "created_at": slot.created_at.isoformat() if slot.created_at else None,
            "snapshot": slot.to_dict()["snapshot"] if slot.snapshot_json else {}
        }
        for slot in save_slots
    ]

class LocationUpsertRequest(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    atmosphere: Optional[str] = None
    exits: List[Dict[str, str]] = []
    immutable: bool = False

@router.post("/locations", response_model=LocationOut)
async def upsert_location_endpoint(request: LocationUpsertRequest, db: Session = Depends(get_db)):
    """Create or update a location"""
    try:
        location_data = {
            "id": request.id,
            "name": request.name,
            "description": request.description,
            "atmosphere": request.atmosphere,
            "exits": request.exits,
            "immutable": request.immutable
        }
        location = upsert_location(db, location_data)
        return LocationOut.model_validate(location.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
