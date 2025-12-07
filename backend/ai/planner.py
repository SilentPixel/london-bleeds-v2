# Planner module - Pass A: Structured planning
from openai import OpenAI
from typing import Dict, Any
from .models import PlannerOutput


def plan_turn(
    openai_client: OpenAI,
    system_prompt: str,
    player_intent: str,
    context_snapshot: Dict[str, Any]
) -> PlannerOutput:
    """
    Generate a structured plan for the player's turn.
    
    Uses low temperature (0.2) for deterministic planning.
    Returns validated JSON conforming to PlannerOutput schema.
    
    Args:
        openai_client: OpenAI client instance
        system_prompt: System prompt template
        player_intent: Player's command/intent
        context_snapshot: Current game state snapshot
    
    Returns:
        PlannerOutput with structured plan
    """
    prompt = f"""{system_prompt}

[PLAYER_INTENT]
{player_intent}

[CONTEXT]
{_format_context(context_snapshot)}

Generate a plan as JSON with:
- "action": string describing the action
- "targets": array of entity IDs involved
- "state_changes": array of {{"entity": "...", "op": "...", "value": ...}}
- "notes": string with any additional notes
"""
    
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt}
        ],
    )
    
    json_content = response.choices[0].message.content
    return PlannerOutput.model_validate_json(json_content)


def _format_context(snapshot: Dict[str, Any]) -> str:
    """Format context snapshot for prompt"""
    lines = []
    if "player" in snapshot:
        lines.append(f"Player: {snapshot['player'].get('profile_name', 'Unknown')}")
        lines.append(f"Location: {snapshot['player'].get('current_location_id', 'Unknown')}")
    if "inventory" in snapshot:
        lines.append(f"Inventory: {len(snapshot['inventory'])} items")
    if "seen_flags" in snapshot:
        lines.append(f"Seen: {len(snapshot['seen_flags'])} entities")
    return "\n".join(lines)

