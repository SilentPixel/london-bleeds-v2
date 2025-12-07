# Ephemeral events utilities
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.models import EphemeralEvent

def purge_ephemeral_by_player(db: Session, player_id: str) -> int:
    """Purge all ephemeral events for a specific player"""
    deleted_count = db.query(EphemeralEvent).filter(EphemeralEvent.player_id == player_id).delete()
    db.commit()
    return deleted_count

def purge_ephemeral_by_location(db: Session, location_id: str) -> int:
    """Purge all ephemeral events for a specific location"""
    deleted_count = db.query(EphemeralEvent).filter(EphemeralEvent.location_id == location_id).delete()
    db.commit()
    return deleted_count

def purge_ephemeral_by_player_and_location(db: Session, player_id: str, location_id: str) -> int:
    """Purge ephemeral events for a specific player and location"""
    deleted_count = db.query(EphemeralEvent).filter(
        and_(
            EphemeralEvent.player_id == player_id,
            EphemeralEvent.location_id == location_id
        )
    ).delete()
    db.commit()
    return deleted_count

def purge_ephemeral_older_than(db: Session, days: int = 1) -> int:
    """Purge ephemeral events older than specified days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    deleted_count = db.query(EphemeralEvent).filter(
        EphemeralEvent.created_at < cutoff_date
    ).delete()
    db.commit()
    return deleted_count

def create_ephemeral_event(db: Session, player_id: str, text: str, location_id: str = None) -> EphemeralEvent:
    """Create a new ephemeral event (temporary AI-generated color that never mutates canon)"""
    ephemeral = EphemeralEvent(
        player_id=player_id,
        location_id=location_id,
        text=text
    )
    db.add(ephemeral)
    db.commit()
    db.refresh(ephemeral)
    return ephemeral


