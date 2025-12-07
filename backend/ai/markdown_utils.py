# Markdown validation utilities
import re
from typing import List


def ensure_markdown_valid(text: str) -> bool:
    """
    Ensure markdown text is valid and follows required format.
    
    Requirements:
    - Must start with ### Scene Header
    - Must contain valid markdown syntax
    
    Args:
        text: Markdown text to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not text or not text.strip():
        return False
    
    # Check if starts with scene header
    if not re.match(r'^#{3}\s+.+', text.strip()):
        return False
    
    # Check for basic markdown elements (optional but good to have)
    # This is a basic check - can be expanded
    
    return True


def extract_scene_header(markdown: str) -> str:
    """Extract scene header from markdown"""
    match = re.match(r'^#{3}\s+(.+)$', markdown.strip(), re.MULTILINE)
    return match.group(1) if match else ""


def extract_next_actions(markdown: str) -> List[str]:
    """Extract next actions list from markdown"""
    actions = []
    in_section = False
    
    for line in markdown.split('\n'):
        if re.search(r'\*\*Next actions?\*\*:', line, re.IGNORECASE):
            in_section = True
            continue
        
        if in_section:
            # Match bullet points
            bullet_match = re.match(r'^[-*]\s*(.+)$', line.strip())
            if bullet_match:
                action = bullet_match.group(1).strip()
                # Clean markdown formatting
                action = re.sub(r'\*\*(.+?)\*\*', r'\1', action)
                action = re.sub(r'_(.+?)_', r'\1', action)
                if action:
                    actions.append(action)
            elif line.strip() and not line.strip().startswith('#'):
                # End of section
                break
    
    return actions


