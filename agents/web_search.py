from .Internet_data_retriever.internet_data import DataRetrievalCrew
from .base import AgentState
from langchain_core.messages import HumanMessage

class WebSearcherAgent:
    def __init__(self, llm):
        self.data_retriever_crew = DataRetrievalCrew
        self.llm = llm

    async def process(self, state: AgentState) -> AgentState:
        result = await self.data_retriever_crew(state["messages"][-1].content, llm=self.llm).run()
     
        return {
            "messages": [HumanMessage(content=result.raw, name="web_searcher")],
            "next": state["caller"],
            "thought_step": state["thought_step"],
            "caller": "web_searcher"
        }
