from .Internet_data_retriever.internet_data import DataRetrievalCrew
from .base import AgentState
from langchain_core.messages import HumanMessage
from crewai import LLM
import os

class WebSearcherAgent:
    def __init__(self, llm):
        self.data_retriever_crew = DataRetrievalCrew
        # Convert LangChain LLM to CrewAI LLM format
        # CrewAI uses LiteLLM which needs the provider prefix
        self.llm = self._convert_to_crewai_llm(llm)

    def _convert_to_crewai_llm(self, langchain_llm):
        """Convert LangChain LLM to CrewAI LLM format"""
        try:
            # Get the model name from LangChain LLM
            model_name = getattr(langchain_llm, 'model_name', None) or getattr(langchain_llm, 'model', 'gemini-1.5-flash')
            
            # Remove 'models/' prefix if present (Gemini API format)
            if model_name.startswith('models/'):
                model_name = model_name.replace('models/', '')
            
            # Get API key from environment
            api_key = os.getenv("GOOGLE_API_KEY")
            
            # Create CrewAI LLM with proper format for Gemini
            # LiteLLM expects format: gemini/<model-name>
            crewai_llm = LLM(
                model=f"gemini/{model_name}",
                api_key=api_key,
                temperature=0.7
            )
            
            return crewai_llm
        except Exception as e:
            print(f"Warning: Could not convert LLM, using default: {e}")
            # Fallback to a working configuration
            return LLM(
                model="gemini/gemini-1.5-flash",
                api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.7
            )

    async def process(self, state: AgentState) -> AgentState:
        # Check web search limit (max 2 searches per workflow)
        current_count = state.get("web_search_count", 0)
        if current_count >= 2:
            print(f"[WEB SEARCH] Limit reached ({current_count}/2), skipping search")
            return {
                "messages": [HumanMessage(content="Web search limit reached. Using existing information.", name="web_searcher")],
                "next": state["caller"],
                "thought_step": state["thought_step"],
                "caller": "web_searcher",
                "web_search_count": current_count  # Keep count
            }
        
        print(f"[WEB SEARCH] Executing search ({current_count + 1}/2)")
        result = await self.data_retriever_crew(state["messages"][-1].content, llm=self.llm).run()
     
        return {
            "messages": [HumanMessage(content=result.raw, name="web_searcher")],
            "next": state["caller"],
            "thought_step": state["thought_step"],
            "caller": "web_searcher",
            "web_search_count": current_count + 1  # Increment count
        }
