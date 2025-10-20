from typing import Dict, List, Optional, Any, TypedDict, Literal
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    """State for each agent node in the graph"""
    next: str  # Where to route to next
    thought_step: Optional[int] = 0  # Current step in chain of thought
    caller: Optional[str] = None  # Who called the agent


def safe_get_content(obj, default: str = "") -> str:
    """
    Safely extract content from an LLM response object.
    Handles cases where content might be a list, string, or other type.
    
    Args:
        obj: The object to extract content from (usually LLM response)
        default: Default value to return if extraction fails
        
    Returns:
        String content or default value
    """
    if obj is None:
        return default
    
    # Try to get content attribute
    if hasattr(obj, 'content'):
        content = obj.content
        # Handle list content
        if isinstance(content, list):
            return ' '.join(str(item) for item in content)
        # Handle string content
        elif isinstance(content, str):
            return content
        # Handle other types
        else:
            return str(content) if content else default
    
    # If no content attribute, try converting object itself
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, list):
        return ' '.join(str(item) for item in obj)
    else:
        return str(obj) if obj else default

