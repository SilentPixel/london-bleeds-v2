# Save and load functionality
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from db.models import Player, Inventory, SeenFlag, SaveSlot
from db.json_utils import dumps, loads

def create_save_snapshot(db: Session, player_id: str) -> dict:
    """Create a snapshot of player state including inventory, seen flags, etc."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return {}
    
    # Get inventory
    inventory = db.query(Inventory).filter(Inventory.player_id == player_id).all()
    inventory_data = [
        {
            "item_id": inv.item_id,
            "quantity": inv.quantity
        }
        for inv in inventory
    ]
    
    # Get seen flags
    seen_flags = db.query(SeenFlag).filter(SeenFlag.player_id == player_id).all()
    seen_flags_data = [
        {
            "entity_kind": sf.entity_kind,
            "entity_id": sf.entity_id,
            "first_seen_at": sf.first_seen_at.isoformat() if sf.first_seen_at else None
        }
        for sf in seen_flags
    ]
    
    snapshot = {
        "player": {
            "id": player.id,
            "profile_name": player.profile_name,
            "current_location_id": player.current_location_id,
            "vars": loads(player.vars_json),
            "created_at": player.created_at.isoformat() if player.created_at else None,
            "updated_at": player.updated_at.isoformat() if player.updated_at else None
        },
        "inventory": inventory_data,
        "seen_flags": seen_flags_data,
        "snapshot_at": datetime.utcnow().isoformat()
    }
    
    return snapshot

def create_save_slot(db: Session, player_id: str, slot_name: str) -> SaveSlot:
    """Create a new save slot for a player"""
    snapshot = create_save_snapshot(db, player_id)
    
    save_slot = SaveSlot(
        id=str(uuid.uuid4()),
        player_id=player_id,
        name=slot_name,
        snapshot_json=dumps(snapshot)
    )
    
    db.add(save_slot)
    db.commit()
    db.refresh(save_slot)
    
    return save_slot

def get_save_slots(db: Session, player_id: str) -> list[SaveSlot]:
    """Get all save slots for a player"""
    return db.query(SaveSlot).filter(SaveSlot.player_id == player_id).order_by(SaveSlot.created_at.desc()).all()

def autosave(player_id: str):
    """Placeholder for autosave functionality (Phase 2+)"""
    # This will be implemented in Phase 2
    # Will be called after turn mutations to automatically save player state
    pass


