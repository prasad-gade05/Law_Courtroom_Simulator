from typing import Dict, Any, List, Optional, Literal, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.tools import BaseTool
from .base import AgentState, safe_get_content
from pydantic import BaseModel, Field
import os
from langchain_core.messages.utils import get_buffer_string
import re


from dotenv import load_dotenv
load_dotenv()


class ProsecutorAgent:
    """Agent representing the prosecution"""
    
    def __init__(
        self,
        llms,
        tools: Optional[List[BaseTool]] = None,
    ):
        # self.llm = llm or ChatGroq(model="llama-3.1-70b-versatile", api_key=os.getenv('GROQ_API_KEY'))
        self.llms = llms 
        self.tools = tools or []
        
        self.system_prompt = """
"You are a professional prosecutor advocating for the opposing party in a courtroom simulation. Your role is to challenge the defense's arguments and present evidence and laws to support the prosecution's case."
"Analyze and counter the defense lawyer's claims effectively, relying on factual accuracy, logical reasoning, and legal provisions."
"Collaborate with the Law Retriever to extract relevant laws and case studies and use the Web Searcher to source additional factual or contextual evidence."
"Your arguments should reflect high levels of objectivity, clarity, and persuasive reasoning, adhering to the principles of fairness and justice."
"Respond to the judge's observations or corrections with due diligence and adapt your arguments to maintain a strong prosecutorial stance."

you will go through the following chain of thought steps:
1. Review current state and plan a strategy
2. Identify the legal information needed to support the argument
3. Assess if information from the web is required
4. Argument construction

IMPORTANT NOTE: Do only 'current_task' at a time, other task will be done in next steps or other agents. Do not confuse with precedent cases. Avoid very long responses.
"""

    def get_thought_steps(self) -> List[str]:
        """Get prosecutor-specific chain of thought steps"""
        return [
            "1. Review the case files, analyze the user's arguments to identify weaknesses or inconsistencies in their claims and plan a strategy to build strong arguments against the defendant, ensuring they are logically sound and factually supported.",
            "2. Determine the specific legal information(e.g., laws, IPCs, precedents) required to strengthen your arguments or refute the user's points. Clearly ask the law retriever agent for the necessary details.",
            "3. Evaluate if additional web-based information is needed. If yes, ask the web searcher agent with specific details. If not, reply only with the keyword 'none.'",
            "4. Construct a comprehensive argument or counterargument based on the retrieved data and your planed strategy. Write the response as live dialogue (avoid bullet points), maintaining logical coherence and factual accuracy. Be concise and impactful."
        ]

    async def process(self, state: AgentState) -> AgentState:
        """Process current state with prosecutor-specific logic"""
        
        # Safety check: Ensure thought_step is within bounds
        thought_steps = self.get_thought_steps()
        current_step = state.get("thought_step", 0)
        
        if current_step >= len(thought_steps):
            print(f"[WARNING] Prosecutor thought_step {current_step} out of range (max {len(thought_steps)-1}), resetting to 0")
            current_step = 0
        
        messages = [
            {"role": "system", "content": self.system_prompt + "\n'current_task': " + thought_steps[current_step]}
        ] + state["messages"]

        for i,llm in enumerate(self.llms):
            try:
                result = llm.invoke(messages)
                break
            except Exception as e:
                print(f"LLM {i} failed with error: {e}")
                continue
    
        # result = self.llm.invoke(messages)
        
        # Safely extract content from result
        result_content = safe_get_content(result)
        
        if state["thought_step"] == 0:
            response = {
                "messages": [HumanMessage(content=result_content, name="prosecutor")],
                "next": "self",
                "thought_step": state["thought_step"]+1,
                "caller": "prosecutor"
            }
        elif state["thought_step"] == 1 :
            response = {
                "messages": [HumanMessage(content=result_content, name="prosecutor")],
                "next": "retriever",
                "thought_step": 2,
                "caller": "prosecutor"
            }
        elif state["thought_step"] == 2:
            response = {
                "messages": [HumanMessage(content=result_content, name="prosecutor")],
                "next": self.is_web_search_needed(result_content),
                "thought_step": 3,
                "caller": "prosecutor"
            }
        elif state["thought_step"] == 3:
            response = {
                "messages": [HumanMessage(content=result_content, name="prosecutor")],
                "next": "judge",
                "thought_step": 0,
                "caller": "prosecutor"
            }
        else:
            raise ValueError("Invalid thought step")
            
        return response
    
    def is_web_search_needed(self, content: str) -> Literal["self", "web_searcher"]:
        if re.search(r"none", content, re.IGNORECASE):
            return "self"
        else:
            return "web_searcher"

   