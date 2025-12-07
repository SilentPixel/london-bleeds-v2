from typing import Optional
import os
import traceback
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from openai import OpenAI

from db.engine import get_db
from db.saves import create_save_snapshot
from ai.context_engine import run_turn
from ai.planner import plan_turn
from ai.narrator import narrate_turn_streaming, _extract_next_actions
from ai.validators import validate_plan
from ai.prompts import SYSTEM_PROMPT
from ai.memory import retrieve_context
from ai.models import NarratorOutput


router = APIRouter()


class PlayRequest(BaseModel):
    command: str
    player_id: Optional[str] = None
    current_location_id: Optional[str] = None


class PlayResponse(BaseModel):
    markdown: str


@router.post("/play", response_model=PlayResponse)
async def play_turn(payload: PlayRequest, db: Session = Depends(get_db)) -> PlayResponse:
    """
    Minimal /play endpoint to drive a single game turn.

    For now this uses a simple snapshot of the given player (or a demo player)
    and runs one turn through the AI context engine.
    """
    player_id = payload.player_id or "demo"

    # Build a snapshot of current player state if possible
    snapshot = create_save_snapshot(db, player_id) or {"player": {"id": player_id}}
    
    # Override location with frontend-provided location if available
    # This ensures backend uses the correct current location from frontend state
    if payload.current_location_id:
        if "player" not in snapshot:
            snapshot["player"] = {}
        snapshot["player"]["current_location_id"] = payload.current_location_id

    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not found in environment variables. Please check your .env file."
        )

    try:
        client = OpenAI(api_key=api_key)
        narrator_output = run_turn(
            openai_client=client,
            player_intent=payload.command,
            snapshot=snapshot,
            db=db,
            turn_id=0,
        )
    except Exception as exc:  # pragma: no cover - surfaced to client
        # Log full traceback for debugging
        error_trace = traceback.format_exc()
        print(f"Error in /play endpoint:\n{error_trace}", flush=True)
        # Return a user-friendly error message
        error_msg = str(exc)
        raise HTTPException(status_code=500, detail=error_msg)

    return PlayResponse(markdown=narrator_output.markdown)


@router.post("/play/stream")
async def play_turn_stream(
    payload: PlayRequest, 
    db: Session = Depends(get_db)
):
    """
    Streaming version of /play endpoint.
    Returns Server-Sent Events (SSE) with narrative chunks for faster perceived performance.
    """
    player_id = payload.player_id or "demo"

    # Build snapshot
    snapshot = create_save_snapshot(db, player_id) or {"player": {"id": player_id}}
    
    if payload.current_location_id:
        if "player" not in snapshot:
            snapshot["player"] = {}
        snapshot["player"]["current_location_id"] = payload.current_location_id

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not found in environment variables."
        )

    try:
        client = OpenAI(api_key=api_key)
        
        # Pass A: Planning (non-streaming, fast)
        relevant_facts = retrieve_context(payload.command)
        system_prompt = SYSTEM_PROMPT.format(
            relevant_facts=relevant_facts if relevant_facts else "(No relevant facts found)"
        )
        planner_output = plan_turn(client, system_prompt, payload.command, snapshot)
        validate_plan(planner_output)
        
        # Pass B: Streaming narration
        async def generate():
            full_text = ""
            try:
                for chunk in narrate_turn_streaming(client, system_prompt, planner_output, snapshot):
                    full_text += chunk
                    # Format as SSE
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                
                # Extract next actions from complete markdown
                next_actions = _extract_next_actions(full_text)
                
                # Send metadata
                yield f"data: {json.dumps({'type': 'metadata', 'next_actions': next_actions})}\n\n"
                
                # Save to database after streaming completes
                from ai.context_engine import _save_transcript_event
                narrator_output = NarratorOutput(markdown=full_text, next_actions=next_actions)
                _save_transcript_event(db, 0, payload.command, planner_output, narrator_output, snapshot)
                
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            except Exception as e:
                error_trace = traceback.format_exc()
                print(f"Error in streaming generation:\n{error_trace}", flush=True)
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            }
        )
        
    except Exception as exc:
        error_trace = traceback.format_exc()
        print(f"Error in /play/stream endpoint:\n{error_trace}", flush=True)
        raise HTTPException(status_code=500, detail=str(exc))


