from typing import Dict, Any, List, Optional, Literal, TypedDict
from langchain_core.messages import HumanMessage
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from agents.base import AgentState, safe_get_content
import re

# class JudgeDecision(BaseModel):
#     """Judge's structured decision output"""
#     response: str = Field(description="The judge's response and comments")
#     next_agent: Literal["lawyer", "prosecutor", "END"] = Field(
#         description="Next agent to speak in the trial or END if verdict is given in response"
#     )

class JudgeAgent:
    """Agent representing the judge who manages the trial flow"""
    
    def __init__(
        self,  
        llms,
        tools: Optional[List[BaseTool]] = None,
    ):
        # self.llm = llm or ChatGroq(model="llama3-8b-8192", api_key=os.getenv('GROQ_API_KEY'))
        self.llms = llms # Multiple LLMs for fallback redundancy
        self.tools = tools or []
        
        # Comprehensive system prompt defining the judge's role and responsibilities
        self.system_prompt = """
"You are a presiding judge overseeing a courtroom simulation. Your primary role is to evaluate the arguments presented by the lawyer and prosecutor for logical consistency, factual accuracy, and adherence to legal principles."
"Point out inconsistencies, hallucinations, or errors in the agents' arguments and provide constructive feedback to help refine them."
"Call upon the Law Retriever and Web Searcher agents as necessary to verify or clarify legal and factual claims made during the arguments."
"Monitor the proceedings and identify when sufficient arguments have been presented and the case is ready for a verdict."
"CRITICAL: Ensure BOTH sides (lawyer AND prosecutor) have equal opportunity to present their case. You MUST alternate between them."
"When deciding next speaker, check who spoke last in the message history and give the OTHER party a turn."
"Summarize the case before delivering a verdict, outlining the key points of contention and the reasoning behind your decision."
"Your decisions and comments should be impartial, grounded in logic, and aimed at maintaining the integrity of the courtroom process."

IMPORTANT INSTRUCTIONS:
1. When ready for verdict, start your response with "VERDICT DELIVERED:"
2. When continuing trial, end your response with "NEXT SPEAKER: lawyer" or "NEXT SPEAKER: prosecutor"
3. Always use the exact format "NEXT SPEAKER: [lawyer/prosecutor]" so routing is clear
4. Do NOT say things like "the next speaker should be" - use the exact format above

you will go through the following chain of thought steps:
1. Review arguments
2. legal data retrieval
3. web search (if needed) 
4. verdict OR route to next speaker

Do ONLY 'current_task', other tasks will be done in next steps or by other agents. Avoid very long responses.
"""

    def get_thought_steps(self) -> List[str]:
        """
        Returns the sequential steps in the judge's decision-making process.
        Each step represents a specific phase of analysis and action.
        """
        return [
            "1. Listen to the arguments presented by both the lawyer and prosecutor. Note their key points and claims. Identify potential hallucinations or logical errors or factual errors in latest argument.",
            "2. Determine the specific legal data (e.g., laws, IPCs, legal case precedents) required for cross verificaton of identified errors. Clearly ask the law retriever agent for the necessary legal data.",
            "3. Evaluate if additional web-based information is needed. If yes, ask the web searcher agent with specific details. If not, reply only with the keyword 'none.'",
            """4. Make final decision for this turn:
            A) VERDICT PATH - If ready for verdict (6+ arguments from each side OR iteration >= 20):
               - IMMEDIATELY deliver verdict starting with exact keyphrase "VERDICT DELIVERED:"
               - Summarize case and state guilty or not guilty
               
            B) CONTINUE TRIAL PATH - If NOT ready for verdict:
               - Provide brief feedback on latest argument
               - Check message history to see who spoke last
               - Respond with ONLY ONE KEYWORD at the end: "lawyer" (if prosecutor spoke last) OR "prosecutor" (if lawyer spoke last)
               - Format: [Your feedback here]. NEXT SPEAKER: lawyer
            
            Be clear and decisive. Do not be ambiguous."""
        ]

    async def process(self, state: AgentState) -> AgentState:
        """
        Process the current state and generate the next state based on judge's logic.
        
        Args:
            state: Current state of the trial containing messages and thought step
            
        Returns:
            Updated state with judge's response and next action
            
        """
        
        # Safety check: Ensure thought_step is within bounds
        thought_steps = self.get_thought_steps()
        current_step = state.get("thought_step", 0)
        
        if current_step >= len(thought_steps):
            print(f"[WARNING] Judge thought_step {current_step} out of range (max {len(thought_steps)-1}), resetting to 0")
            current_step = 0
        
        # Prepare messages for LLM processing
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + state["messages"] + [{"role": "system", "content": f"current_task: {thought_steps[current_step]}" }]
        # print(messages)
        # Process through LLMs with fallback mechanism
        # if state["thought_step"] != 4:
        for i, llm in enumerate(self.llms):
            try:
                result = llm.invoke(messages)
                break
            except Exception as e:
                print(f"LLM {i} failed with error: {e}")
                continue

        #     # result = self.llm.invoke(messages)
        # else:
        #     # Special handling for final decision step
        #     for i,llm in enumerate(self.llms):
        #         try:
        #             result = llm.with_structured_output(JudgeDecision).invoke(messages)
        #             break
        #         except Exception as e:
        #             print(f"LLM {i} failed with error: {e}")
        #             continue
            # result = self.llm.with_structured_output(JudgeDecision).invoke(messages)
        
        # Safely extract content from result
        result_content = safe_get_content(result)
        
        if state["thought_step"] == 0 or state["thought_step"] == 2:
            # Initial review or post-web search steps
            response = {
                "messages": [HumanMessage(content=result_content, name="judge")],
                "next": "self",
                "thought_step": state["thought_step"]+1,
                "caller": "judge"
            }
        elif state["thought_step"] == 1:
            # Legal data retrieval step
            response = {
                "messages": [HumanMessage(content=result_content, name="judge") ],
                "next": self.determine_after_legal_data(result_content),
                "thought_step": 2 if self.determine_after_legal_data(result_content) == "retriever" else 3,
                "caller": "judge"
            }
        elif state["thought_step"] == 3:
            # Final decision: Verdict OR route to next speaker
            # Check if verdict was delivered
            if "VERDICT DELIVERED" in result_content:
                response = {
                    "messages": [HumanMessage(content=result_content, name="judge")],
                    "next": "END",
                    "thought_step": 0,
                    "caller": "judge"
                }
            else:
                # No verdict - determine next speaker from content
                next_dest = self.extract_next_speaker(result_content, state)
                response = {
                    "messages": [HumanMessage(content=result_content, name="judge")],
                    "next": next_dest,
                    "thought_step": 0,
                    "caller": "judge"
                }
        else:
            raise ValueError(f"Invalid thought step: {state['thought_step']}")

        return response
    
    def determine_after_legal_data(self, content: str) -> Literal["self", "retriever"]:
        """
        Determines if legal data retrieval is needed based on the content.
        Returns 'retriever' if needed, 'self' otherwise.
        """
        if "none" in content.lower() or "no legal data" in content.lower():
            return "self"
        else:
            return "retriever"
    
    def is_web_search_needed(self, content: str) -> Literal["self", "web_searcher"]:
        """
        Determines if web search is needed based on the content.
        Returns 'self' if no search needed, 'web_searcher' otherwise.
        """
        if "none" in content.lower():
            return "self"
        else:
            return "web_searcher"
    
    def extract_next_speaker(self, content: str, state: AgentState) -> Literal["lawyer", "prosecutor", "END"]:
        """
        Extract the next speaker from judge's response.
        Handles multiple formats:
        - "NEXT SPEAKER: lawyer"
        - "The next speaker should be the lawyer"
        - "lawyer" (keyword)
        Also checks iteration count as failsafe.
        """
        content_lower = content.lower()
        
        # Check iteration count as failsafe for termination
        iteration = state.get("iteration_count", 0)
        if iteration >= 24:
            print(f"[JUDGE] Iteration {iteration} >= 24, forcing END")
            return "END"
        
        # Look for explicit patterns
        if "next speaker:" in content_lower:
            # Extract after "NEXT SPEAKER:"
            parts = content_lower.split("next speaker:")
            if len(parts) > 1:
                speaker_text = parts[1].strip().split()[0]  # Get first word
                if "lawyer" in speaker_text:
                    return "lawyer"
                elif "prosecutor" in speaker_text:
                    return "prosecutor"
        
        # Look for "the next speaker should be the [lawyer/prosecutor]"
        if "defense lawyer" in content_lower or ("next" in content_lower and "lawyer" in content_lower):
            return "lawyer"
        if "next" in content_lower and "prosecutor" in content_lower:
            return "prosecutor"
        
        # Direct keyword search (with exclusion to avoid false positives)
        if "lawyer" in content_lower and "prosecutor" not in content_lower:
            return "lawyer"
        elif "prosecutor" in content_lower and "lawyer" not in content_lower:
            return "prosecutor"
        
        # If no clear indication, check message history to alternate
        messages = state.get("messages", [])
        if messages:
            for msg in reversed(messages):
                msg_name = ""
                if hasattr(msg, 'name'):
                    msg_name = msg.name
                elif isinstance(msg, dict) and 'name' in msg:
                    msg_name = msg['name']
                
                if msg_name == "prosecutor":
                    print(f"[JUDGE] Last speaker was prosecutor, routing to lawyer")
                    return "lawyer"
                elif msg_name == "lawyer":
                    print(f"[JUDGE] Last speaker was lawyer, routing to prosecutor")
                    return "prosecutor"
        
        # Default: give lawyer first turn (fair trial principle)
        print(f"[JUDGE] No clear routing found, defaulting to lawyer")
        return "lawyer"
        
    def next_speaker(self, content: str, state: AgentState) -> Literal["lawyer", "prosecutor", "END"]:
        """
        Determines the next speaker based on the content and state.
        Checks for END first (verdict), then looks at message history to alternate fairly.
        """
        content_lower = content.lower()
        
        # Check for END/verdict keywords first
        if any(keyword in content_lower for keyword in ["end", "verdict delivered", "trial concluded"]):
            return "END"
        
        # Check iteration count as failsafe
        iteration = state.get("iteration_count", 0)
        if iteration >= 24:
            return "END"
        
        # Check for specific agent routing in content
        if "lawyer" in content_lower and "prosecutor" not in content_lower:
            return "lawyer"
        elif "prosecutor" in content_lower and "lawyer" not in content_lower:
            return "prosecutor"
        
        # Look at message history to determine who spoke last
        messages = state.get("messages", [])
        if messages:
            # Search backwards for the last lawyer or prosecutor message
            for msg in reversed(messages):
                # Get the name/role from message
                msg_name = ""
                if hasattr(msg, 'name'):
                    msg_name = msg.name
                elif isinstance(msg, dict) and 'name' in msg:
                    msg_name = msg['name']
                
                # Alternate based on last speaker
                if msg_name == "prosecutor":
                    return "lawyer"  # Give lawyer a turn
                elif msg_name == "lawyer":
                    return "prosecutor"  # Give prosecutor a turn
        
        # Default: if no clear pattern, start with lawyer (defense goes first in many systems)
        return "lawyer"
