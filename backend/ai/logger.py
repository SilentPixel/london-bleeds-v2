# Logging utilities for AI turns
import datetime
import json
import os
from pathlib import Path
from typing import Dict, Any
from .models import PlannerOutput, NarratorOutput


def log_turn(
    turn_id: int,
    planner: PlannerOutput,
    narrator: NarratorOutput
) -> None:
    """
    Log turn output to filesystem.
    
    Creates:
    - logs/turn_{turn_id}.md - Markdown narrative
    - logs/turn_{turn_id}.json - Planner metadata
    
    Args:
        turn_id: Turn number
        planner: Planner output
        narrator: Narrator output
    """
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Write Markdown file
    md_path = logs_dir / f"turn_{turn_id}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(narrator.markdown)
    
    # Write metadata JSON
    meta = {
        "turn": turn_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "planner": planner.model_dump(),
        "next_actions": narrator.next_actions,
    }
    
    json_path = logs_dir / f"turn_{turn_id}.json"
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(meta, jf, indent=2, ensure_ascii=False)

