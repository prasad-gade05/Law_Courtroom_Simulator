# --- FINAL MODIFIED agents/web_search.py ---

from .Internet_data_retriever.internet_data import DataRetrievalCrew
from .base import AgentState
from langchain_core.messages import HumanMessage
# We no longer need to import crewai's LLM wrapper
# from crewai import LLM 
import os

class WebSearcherAgent:
    def __init__(self, llm):
        self.data_retriever_crew = DataRetrievalCrew
        
        # --- THE FIX ---
        # We no longer convert the LLM. We just store the raw LangChain object.
        # CrewAI agents can use LangChain LLMs directly.
        self.llm = llm
        print("[WebSearcherAgent] Initialized using the provided LangChain LLM object directly.")
        # --- END OF FIX ---

    # --- THE FIX ---
    # The entire problematic conversion function is now deleted.
    # --- END OF FIX ---

    async def process(self, state: AgentState) -> AgentState:
        # Check web search limit (max 3 searches per workflow)
        current_count = state.get("web_search_count", 0)
        if current_count >= 3:
            print(f"[WEB SEARCH] Limit reached ({current_count}/3), skipping search")
            return {
                "messages": [HumanMessage(content="Web search limit reached. Using existing information.", name="web_searcher")],
                "next": state["caller"],
                "thought_step": state["thought_step"],
                "caller": "web_searcher",
                "web_search_count": current_count  # Keep count
            }
        
        print(f"[WEB SEARCH] Executing search ({current_count + 1}/3)")
        
        try:
            # Get the latest message content for search
            latest_message = state["messages"][-1].content if state["messages"] else ""
            
            if not latest_message or len(latest_message.strip()) < 10:
                print(f"[WEB SEARCH] Insufficient content for search, skipping")
                return {
                    "messages": [HumanMessage(content="Insufficient content for web search. Using existing information.", name="web_searcher")],
                    "next": state["caller"],
                    "thought_step": state["thought_step"],
                    "caller": "web_searcher",
                    "web_search_count": current_count
                }
            
            # Execute web search with error handling
            result = await self.data_retriever_crew(latest_message, llm=self.llm).run()
            
            # Extract content safely
            search_content = ""
            if hasattr(result, 'raw') and result.raw:
                search_content = str(result.raw)
            elif hasattr(result, 'content') and result.content:
                search_content = str(result.content)
            elif isinstance(result, str):
                search_content = result
            else:
                search_content = "Web search completed but no content retrieved."
            
            # Ensure we have meaningful content
            if len(search_content.strip()) < 20:
                search_content = "Web search completed but returned minimal information. Proceeding with available data."
            
            return {
                "messages": [HumanMessage(content=search_content, name="web_searcher")],
                "next": state["caller"],
                "thought_step": state["thought_step"],
                "caller": "web_searcher",
                "web_search_count": current_count + 1  # Increment count
            }
            
        except Exception as e:
            print(f"[WEB SEARCH] Error during search: {e}")
            return {
                "messages": [HumanMessage(content=f"Web search failed: {str(e)}. Proceeding with available information.", name="web_searcher")],
                "next": state["caller"],
                "thought_step": state["thought_step"],
                "caller": "web_searcher",
                "web_search_count": current_count + 1  # Still increment to prevent infinite retries
            }