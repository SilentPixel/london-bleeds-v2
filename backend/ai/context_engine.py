# AI Context Engine - Main orchestration
from typing import Dict, Any
from openai import OpenAI
from sqlalchemy.orm import Session

from .models import PlannerOutput, NarratorOutput
from .planner import plan_turn
from .narrator import narrate_turn
from .prompts import SYSTEM_PROMPT
from .validators import validate_plan, check_red_lines
from .logger import log_turn
from .markdown_utils import ensure_markdown_valid
from .memory import retrieve_context


def run_turn(
    openai_client: OpenAI,
    player_intent: str,
    snapshot: Dict[str, Any],
    db: Session,
    turn_id: int = 0
) -> NarratorOutput:
    """
    Execute a full turn through the AI Context Engine.
    
    Two-pass flow:
    1. Planner (Pass A) - Low temperature, structured JSON output
    2. Narrator (Pass B) - Higher temperature, Markdown narrative
    
    Args:
        openai_client: OpenAI client instance
        player_intent: Player's command/intent
        snapshot: Current game state snapshot
        db: Database session
        turn_id: Turn number for logging
    
    Returns:
        NarratorOutput with markdown narrative
    """
    # Retrieve relevant facts from memory
    relevant_facts = retrieve_context(player_intent)
    system_prompt = SYSTEM_PROMPT.format(relevant_facts=relevant_facts if relevant_facts else "(No relevant facts found)")
    
    # Pass A: Planning
    planner_output = plan_turn(openai_client, system_prompt, player_intent, snapshot)
    validate_plan(planner_output)
    
    # Pass B: Narration
    narrator_output = narrate_turn(openai_client, system_prompt, planner_output, snapshot)
    
    # Validate Markdown format
    if not ensure_markdown_valid(narrator_output.markdown):
        raise ValueError("Narrator output is not valid Markdown")
    
    # Check red-line rules
    red_line_errors = check_red_lines(narrator_output.markdown, snapshot)
    if red_line_errors:
        raise ValueError(f"Red-line violations: {', '.join(red_line_errors)}")
    
    # Log to filesystem
    log_turn(turn_id, planner_output, narrator_output)
    
    # Insert into transcript_events table
    _save_transcript_event(db, turn_id, player_intent, planner_output, narrator_output, snapshot)
    
    return narrator_output


def _save_transcript_event(
    db: Session,
    turn_id: int,
    player_intent: str,
    planner: PlannerOutput,
    narrator: NarratorOutput,
    snapshot: Dict[str, Any]
) -> None:
    """Save transcript event to database"""
    from db.models import TranscriptEvent
    from db.json_utils import dumps
    
    # Get player_id from snapshot
    player_id = snapshot.get("player", {}).get("id", "unknown")
    
    # Create payload with planner data and snapshot context
    payload = {
        "player_intent": player_intent,
        "planner": planner.model_dump(),
        "next_actions": narrator.next_actions,
        "context": snapshot
    }
    
    transcript_event = TranscriptEvent(
        player_id=player_id,
        turn=turn_id,
        kind="narration",
        payload_json=dumps(payload),
        markdown=narrator.markdown
    )
    
    db.add(transcript_event)
    db.commit()

