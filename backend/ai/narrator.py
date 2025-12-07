# Narrator module - Pass B: Markdown narrative generation
from openai import OpenAI
from typing import Dict, Any, List
from .models import PlannerOutput, NarratorOutput
import re


def narrate_turn(
    openai_client: OpenAI,
    system_prompt: str,
    validated_plan: PlannerOutput,
    context_snapshot: Dict[str, Any]
) -> NarratorOutput:
    """
    Generate Markdown-formatted narrative prose.
    
    Uses higher temperature (0.6) for creative narrative.
    Follows canonical rules and system prompt formatting.
    
    Args:
        openai_client: OpenAI client instance
        system_prompt: System prompt template
        validated_plan: Validated plan from Pass A
        context_snapshot: Current game state snapshot
    
    Returns:
        NarratorOutput with Markdown narrative
    """
    composed_prompt = f"""{system_prompt}

[VALIDATED_PLAN]
{validated_plan.model_dump_json(indent=2)}

[CONTEXT]
{_format_context(context_snapshot)}

Generate a Markdown-formatted narrative following the formatting rules.
Must start with ### Scene Header.
End with **Next actions:** section with suggested commands.
"""
    
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        temperature=0.6,
        messages=[
            {"role": "system", "content": composed_prompt}
        ],
    )
    
    markdown_text = response.choices[0].message.content
    
    # Extract next actions from markdown
    next_actions = _extract_next_actions(markdown_text)
    
    return NarratorOutput(
        markdown=markdown_text,
        next_actions=next_actions
    )


def _format_context(snapshot: Dict[str, Any]) -> str:
    """Format context snapshot for prompt"""
    lines = []
    if "player" in snapshot:
        lines.append(f"Player: {snapshot['player'].get('profile_name', 'Unknown')}")
        lines.append(f"Current Location: {snapshot['player'].get('current_location_id', 'Unknown')}")
    if "inventory" in snapshot:
        inventory = snapshot['inventory']
        if isinstance(inventory, list):
            # Handle both list of dicts and list of strings
            items = []
            for item in inventory:
                if isinstance(item, dict):
                    items.append(item.get('item_id', ''))
                else:
                    items.append(str(item))
            if items:
                lines.append(f"Inventory: {', '.join(items)}")
    return "\n".join(lines)


def _extract_next_actions(markdown: str) -> List[str]:
    """Extract next actions from markdown text"""
    actions = []
    in_next_section = False
    
    for line in markdown.split('\n'):
        if '**Next actions:**' in line or '**Next Actions:**' in line:
            in_next_section = True
            continue
        if in_next_section:
            # Match bullet points
            match = re.match(r'^[-\*]\s*(.+)$', line.strip())
            if match:
                action = match.group(1).strip()
                # Remove markdown formatting
                action = re.sub(r'\*\*(.+?)\*\*', r'\1', action)
                action = re.sub(r'_(.+?)_', r'\1', action)
                if action:
                    actions.append(action)
            elif line.strip() and not line.strip().startswith('#'):
                # Stop at next section
                break
    
    return actions


def narrate_turn_streaming(
    openai_client: OpenAI,
    system_prompt: str,
    validated_plan: PlannerOutput,
    context_snapshot: Dict[str, Any]
):
    """
    Generate Markdown-formatted narrative prose with streaming.
    
    Yields chunks of text as they're generated.
    
    Args:
        openai_client: OpenAI client instance
        system_prompt: System prompt template
        validated_plan: Validated plan from Pass A
        context_snapshot: Current game state snapshot
    
    Yields:
        str: Chunks of markdown text as they're generated
    """
    composed_prompt = f"""{system_prompt}

[VALIDATED_PLAN]
{validated_plan.model_dump_json(indent=2)}

[CONTEXT]
{_format_context(context_snapshot)}

Generate a Markdown-formatted narrative following the formatting rules.
Must start with ### Scene Header.
End with **Next actions:** section with suggested commands.
"""
    
    stream = openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        temperature=0.6,
        messages=[
            {"role": "system", "content": composed_prompt}
        ],
        stream=True,  # Enable streaming
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            yield content

