from typing import Dict, List, Optional, Any, TypedDict, Literal
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    """State for each agent node in the graph"""
    next: str  # Where to route to next
    thought_step: Optional[int] = 0  # Current step in chain of thought
    caller: Optional[str] = None  # Who called the agent
    iteration_count: Optional[int] = 0  # Track debate iterations
    initial_retrieval_done: Optional[bool] = False  # Track if initial document fetch is complete
    retrieved_context: Optional[str] = ""  # Store retrieved legal context for all agents
    retrieved_docs: Optional[List] = None  # Store actual document objects for verification


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


def format_messages_for_llm(messages: List[Any]) -> List[Dict[str, str]]:
    """
    Format message history for the LLM.
    Prefixes each message content with its sender to ensure the LLM
    unambiguously knows who spoke in the conversation history.
    """
    formatted = []
    for msg in messages:
        role = "user"
        msg_name = getattr(msg, "name", "") or (msg.get("name", "") if isinstance(msg, dict) else "")
        
        # Determine prefix and role
        prefix = ""
        if msg_name == "lawyer":
            prefix = "[DEFENSE LAWYER]: "
        elif msg_name == "prosecutor":
            prefix = "[PROSECUTION PROSECUTOR]: "
        elif msg_name == "judge":
            prefix = "[JUDGE]: "
            role = "assistant"
        elif msg_name == "kanoon_fetcher":
            prefix = "[KANOON FETCHED CASES]: "
        elif msg_name == "document_summarizer":
            prefix = "[DOCUMENT SUMMARIZER]: "
        elif msg_name == "initial_retriever":
            prefix = "[DOCUMENT RETRIEVER]: "
        
        content = safe_get_content(msg)
        formatted.append({
            "role": role,
            "content": f"{prefix}{content}"
        })
    return formatted

