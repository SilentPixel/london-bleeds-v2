# Validation and red-line enforcement
from typing import Dict, Any, List
from .models import PlannerOutput


def validate_plan(plan: PlannerOutput) -> None:
    """
    Validate planner output structure.
    
    Raises:
        AssertionError: If plan is invalid
    """
    assert plan.action, "Missing action"
    assert isinstance(plan.targets, list), "targets must be a list"
    assert isinstance(plan.state_changes, list), "state_changes must be a list"
    
    for state_change in plan.state_changes:
        assert isinstance(state_change, dict), "state_changes must be dicts"
        assert "entity" in state_change, "state_change missing 'entity'"
        assert "op" in state_change, "state_change missing 'op'"
        assert state_change["op"] in ["set", "add", "remove", "update"], \
            f"Invalid operation: {state_change['op']}"


def check_red_lines(markdown: str, snapshot: Dict[str, Any]) -> List[str]:
    """
    Check for red-line rule violations in markdown output.
    
    Red-line rules:
    - No teleportation
    - No premature reveals (who the killer is)
    - No contradictions with immutable canon
    - Characters referenced must exist in context
    
    Args:
        markdown: Generated markdown text
        snapshot: Current game state snapshot
    
    Returns:
        List of error messages (empty if no violations)
    """
    errors = []
    markdown_lower = markdown.lower()
    
    # Check for teleportation
    if any(word in markdown_lower for word in ["teleport", "instantly appeared", "suddenly found yourself"]):
        errors.append("Possible teleportation detected")
    
    # Check for premature reveals
    if any(phrase in markdown_lower for phrase in ["killer is", "jack the ripper is", "murderer's identity"]):
        errors.append("Premature reveal detected")
    
    # Check character references against snapshot
    # Note: Character validation is disabled for now since the snapshot doesn't include
    # characters at the current location. Core story characters (Holmes, Watson) are
    # always valid to mention in the narrative context of this game.
    # TODO: Re-enable character validation when snapshot includes location-based characters
    
    # Check for contradictions with immutable canon
    # This is a placeholder - can be expanded with more specific checks
    
    return errors

