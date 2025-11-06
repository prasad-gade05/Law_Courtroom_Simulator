from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, MessagesState

class AgentState(MessagesState):
    """State for each agent node in the graph"""
    next: str  # Where to route to next
    thought_step: Optional[int] = 0  # Current step in chain of thought
    caller: Optional[str] = None  # Who called the agent
    iteration_count: Optional[int] = 0  # Total workflow iterations
    web_search_count: Optional[int] = 0  # Count of web searches used
    initial_retrieval_done: Optional[bool] = False  # Track if initial document fetch is complete
    retrieved_context: Optional[str] = ""  # Store retrieved legal context for all agents