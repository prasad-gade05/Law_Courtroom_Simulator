from typing import Dict, Any, List, Optional, Literal, TypedDict
from langchain_core.messages import HumanMessage
from langchain.tools import BaseTool
from .base import AgentState
import re


class LawyerAgent:
    """Agent representing the defense counsel"""
    
    def __init__(
        self,
        llms,
        tools: Optional[List[BaseTool]] = None,
        # **kwargs
    ):
        # self.llm = llm or ChatGroq(model="llama3-8b-8192", api_key=os.getenv('GROQ_API_KEY'))
        self.llms = llms
        self.tools = tools or []
        
        self.system_prompt = """
"You are a professional defense lawyer representing your client in a courtroom simulation. Your primary role is to advocate for the user by presenting strong arguments based on facts, logic, and relevant laws."
"Engage with the prosecutor's claims critically and counter them with well-reasoned arguments, using data and precedents where applicable."
"When required, call upon the Law Retriever to cite specific legal sections or precedents from the vector database and the Web Searcher to gather real-world information supporting your case."
"Ensure that your arguments are respectful, concise, and convincing, maintaining the highest standards of professionalism."
"If your argument contains inconsistencies or errors pointed out by the judge, refine and correct them promptly while maintaining your client's position."

you will go through the following chain of thought steps:
1. Review current state and plan a strategy
2. Identify the legal information needed to support the argument
3. Assess if information from the web is required
4. Argument construction
    <user input>
5. Argument refinement based on feedback

IMPORTANT NOTE: Do only 'current_task' at a time, other task will be done in next steps or other agents. Do not confuse with precedent cases. Avoid very long responses.
"""

    def get_thought_steps(self) -> List[str]:
        """Get lawyer-specific chain of thought steps"""
        return [
            "1. Go through the case files and current state of the courtroom. Plan a strategy to make a strong argument in favor of the user.",
            "2. Identify the specific information needed to support the argument (e.g., laws, IPCs, precedents). Clearly ask the law retriever agent for this information.",
            "3. Assess if additional information from the web is required. If yes, ask the web searcher agent with specific details. If not, reply only with the keyword 'none.'",
            "4. Construct a coherent and persuasive argument based on data received and the planned strategy. Write the response as live dialogue (avoid bullet points), and ensure it is fact-based and free from hallucinations.",
            "5. Refine your argument based on feedback from the user input. if any new points include them to the argument carefully. Correct any inconsistencies or errors pointed out and strengthen your position."

        ]

    async def process(self, state: AgentState) -> AgentState:
        """Process current state with lawyer-specific logic"""
        
        messages = [
            {"role": "system", "content": self.system_prompt + "\n'current_task': " + self.get_thought_steps()[state["thought_step"]]}
        ] + state["messages"] 

        for i,llm in enumerate(self.llms):
            try:
                result = llm.invoke(messages)
                break
            except Exception as e:
                print(f"LLM {i} failed with error: {e}")
                continue

        # result = self.llm.invoke(messages)
        
        if state["thought_step"] == 0:
            response = {
                "messages": [HumanMessage(content=result.content, name="lawyer")],
                "next": "self",
                "thought_step": state["thought_step"]+1,
                "caller": "lawyer"
            }
        elif state["thought_step"] == 1:
            response = {
                "messages": [HumanMessage(content=result.content, name="lawyer")],
                "next": "retriever",
                "thought_step": 2,
                "caller": "lawyer"
            }
        elif state["thought_step"] == 2:
            response = {
                "messages": [HumanMessage(content=result.content, name="lawyer")],
                "next": self.is_web_search_needed(result.content),
                "thought_step": 3,
                "caller": "lawyer"
            }
        elif state["thought_step"] == 3:
            response = {
                "messages": [HumanMessage(content=result.content, name="lawyer")],
                "next": "user_feedback",
                "thought_step": 4,
                "caller": "lawyer"
            }
        elif state["thought_step"] == 4:
            response = {
                "messages": [HumanMessage(content=result.content, name="lawyer")],
                "next": "judge",
                "thought_step": 0,
                "caller": "lawyer"
            }
        else:
            raise ValueError("Invalid thought step")
        return response
    
    def is_web_search_needed(self, content: str) -> Literal["self", "web_searcher"]:
        if re.search(r"none", content, re.IGNORECASE):
            return "self"
        else:
            return "web_searcher"