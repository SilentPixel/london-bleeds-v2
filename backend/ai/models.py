# Pydantic models for AI Context Engine
from pydantic import BaseModel, Field
from typing import List, Dict, Any


class PlannerOutput(BaseModel):
    """Output from the planning pass"""
    action: str = Field(..., description="The action being taken")
    targets: List[str] = Field(default_factory=list, description="Target entities involved")
    state_changes: List[Dict[str, Any]] = Field(default_factory=list, description="Proposed state changes")
    notes: str = Field(default="", description="Additional notes about the plan")


class NarratorOutput(BaseModel):
    """Output from the narration pass"""
    markdown: str = Field(..., description="Markdown-formatted narrative text")
    next_actions: List[str] = Field(default_factory=list, description="Suggested next actions")


