# Debug routes for testing AI turns
from fastapi import APIRouter, Depends, HTTPException
from pathlib import Path
from typing import Dict, Any
from db.engine import get_db
from db.models import TranscriptEvent
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/last_turn")
async def get_last_turn(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get the latest transcript event with Markdown narration.
    
    Returns:
        Dict with markdown text and metadata
    """
    # Get the latest event from database
    latest_event = (
        db.query(TranscriptEvent)
        .order_by(TranscriptEvent.created_at.desc())
        .first()
    )
    
    if not latest_event:
        raise HTTPException(status_code=404, detail="No transcript events found")
    
    return {
        "turn": latest_event.turn,
        "player_id": latest_event.player_id,
        "markdown": latest_event.markdown,
        "created_at": latest_event.created_at.isoformat() if latest_event.created_at else None,
        "payload": latest_event.to_dict().get("payload", {})
    }


@router.get("/turns/{player_id}")
async def get_player_turns(player_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get all transcript events for a specific player.
    
    Returns:
        List of events with markdown
    """
    events = (
        db.query(TranscriptEvent)
        .filter(TranscriptEvent.player_id == player_id)
        .order_by(TranscriptEvent.turn.desc())
        .all()
    )
    
    return {
        "player_id": player_id,
        "count": len(events),
        "events": [
            {
                "turn": event.turn,
                "kind": event.kind,
                "markdown": event.markdown,
                "created_at": event.created_at.isoformat() if event.created_at else None
            }
            for event in events
        ]
    }


