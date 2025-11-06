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
You are a presiding judge overseeing a courtroom simulation. Your primary role is to evaluate the arguments presented by the lawyer and prosecutor for logical consistency, factual accuracy, and adherence to legal principles.

CRITICAL JUDGE RULES:
1. You are NOT a researcher - you do NOT request legal data or web searches
2. You evaluate arguments based on your existing legal knowledge
3. You point out inconsistencies, hallucinations, or errors in the agents' arguments
4. You provide constructive feedback to help refine arguments
5. You monitor proceedings and identify when sufficient arguments have been presented
6. You ensure BOTH sides (lawyer AND prosecutor) have equal opportunity to present their case
7. You alternate between them fairly based on who spoke last
8. You have the authority to conclude the trial when both sides have fully presented their case

ITERATION AWARENESS:
- Current iteration: {iteration}
- If iteration >= 15: Encourage both parties to prepare closing arguments
- If iteration >= 18: Strongly signal that it's time for final statements
- If iteration >= 20: You MUST conclude the trial and proceed to verdict

NATURAL TRIAL CONCLUSION - YOUR KEY RESPONSIBILITY:
- Actively monitor if both sides are starting to repeat themselves or have exhausted their arguments
- Look for signs that the debate has reached a natural conclusion (e.g., "I rest my case", "no further arguments", repetitive points)
- At iteration 15+, start encouraging parties to wrap up
- At iteration 18+, indicate it's time for closing statements
- At iteration 20, you MUST conclude: "Both sides have had ample opportunity to present their case. The court will now proceed to verdict. NEXT: verdict"
- Trust your judgment as a judge - conclude when arguments are exhausted

ROUTING INSTRUCTIONS:
- When continuing trial, end with "NEXT SPEAKER: lawyer" or "NEXT SPEAKER: prosecutor"  
- When you determine the debate has naturally concluded, end with "NEXT: verdict"
- Check message history to see who spoke last and give the OTHER party a turn
- Use exact format "NEXT SPEAKER: [lawyer/prosecutor]" or "NEXT: verdict" for clear routing
- BE DECISIVE: If you sense the trial has run its natural course, conclude it confidently

Do NOT request information from retriever or web searcher agents. Evaluate based on existing knowledge.
"""

    def get_thought_steps(self) -> List[str]:
        """
        Returns the sequential steps in the judge's decision-making process.
        Each step represents a specific phase of analysis and action.
        """
        return [
            "1. Review the arguments presented by both the lawyer and prosecutor. Note their key points and claims. Identify potential hallucinations, logical errors, or factual errors in the latest argument.",
            "2. Evaluate the arguments based on your legal knowledge. Do NOT request additional information. Assess the strength of each side's case and identify any weaknesses or inconsistencies.",
            "3. Determine if the case is ready for verdict phase. Consider: Have both sides made substantial arguments? Are they starting to repeat themselves? Have key legal points been addressed? If the debate feels complete and natural, route to verdict by saying 'NEXT: verdict'. If more discussion is needed, provide brief feedback and determine next speaker.",
            """4. Make final decision for this turn:
            A) VERDICT PATH - If the debate has reached its natural conclusion:
               - Both sides have presented comprehensive arguments
               - Arguments are becoming repetitive or no new substantial points are being made
               - Key legal issues have been thoroughly addressed
               - You sense the trial has run its natural course
               - Say "Both sides have presented their arguments comprehensively. NEXT: verdict" to route to final verdict phase
               
            B) CONTINUE TRIAL PATH - If more meaningful debate is possible:
               - Provide brief feedback on latest argument
               - Check message history to see who spoke last  
               - Respond with: [Your feedback here]. NEXT SPEAKER: [lawyer/prosecutor]
               - Format: [Your feedback here]. NEXT SPEAKER: lawyer
            
            Be decisive and trust your judicial instincts. A good judge knows when a case has been fully argued."""
        ]

    async def process(self, state: AgentState) -> AgentState:
        """
        Process the current state and generate the next state based on judge's logic.
        
        Args:
            state: Current state of the trial containing messages and thought step
            
        Returns:
            Updated state with judge's response and next action
            
        """
        
        # Get iteration count for context
        iteration = state.get("iteration_count", 0)
        
        # Safety check: Ensure thought_step is within bounds
        thought_steps = self.get_thought_steps()
        current_step = state.get("thought_step", 0)
        
        if current_step >= len(thought_steps):
            print(f"[WARNING] Judge thought_step {current_step} out of range (max {len(thought_steps)-1}), resetting to 0")
            current_step = 0
        
        # Prepare messages for LLM processing with iteration context
        enhanced_prompt = self.system_prompt.format(iteration=iteration)
        messages = [
            {"role": "system", "content": enhanced_prompt}
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
        
        # Ensure we have meaningful content
        if not result_content or len(result_content.strip()) < 10:
            result_content = "The court is reviewing the arguments and will provide guidance."
        
        if state["thought_step"] == 0:
            # Initial review step
            response = {
                "messages": [HumanMessage(content=result_content, name="judge")],
                "next": "self",
                "thought_step": state["thought_step"]+1,
                "caller": "judge",
                "iteration_count": iteration
            }
        elif state["thought_step"] == 1:
            # Evaluation step
            response = {
                "messages": [HumanMessage(content=result_content, name="judge")],
                "next": "self",
                "thought_step": state["thought_step"]+1,
                "caller": "judge",
                "iteration_count": iteration
            }
        elif state["thought_step"] == 2:
            # Decision step
            response = {
                "messages": [HumanMessage(content=result_content, name="judge")],
                "next": "self",
                "thought_step": state["thought_step"]+1,
                "caller": "judge",
                "iteration_count": iteration
            }
        elif state["thought_step"] == 3:
            # Final decision: Verdict OR route to next speaker
            # Increment iteration when routing to next agent (new debate turn)
            next_iteration = iteration + 1
            
            # Check if verdict was delivered
            if "VERDICT DELIVERED" in result_content:
                response = {
                    "messages": [HumanMessage(content=result_content, name="judge")],
                    "next": "END",
                    "thought_step": 0,
                    "caller": "judge",
                    "iteration_count": next_iteration
                }
            else:
                # No verdict - determine next speaker from content
                next_dest = self.extract_next_speaker(result_content, state)
                response = {
                    "messages": [HumanMessage(content=result_content, name="judge")],
                    "next": next_dest,
                    "thought_step": 0,
                    "caller": "judge",
                    "iteration_count": next_iteration
                }
        else:
            raise ValueError(f"Invalid thought step: {state['thought_step']}")

        return response
    
    
    def extract_next_speaker(self, content: str, state: AgentState) -> Literal["lawyer", "prosecutor", "verdict", "END"]:
        """
        Extract the next speaker from judge's response.
        Handles multiple formats:
        - "NEXT SPEAKER: lawyer"
        - "NEXT: verdict"
        - "The next speaker should be the lawyer"
        - "lawyer" (keyword)
        Also checks iteration count as failsafe.
        """
        content_lower = content.lower()
        
        # Check for verdict routing
        if "next: verdict" in content_lower or "route to verdict" in content_lower or "verdict phase" in content_lower:
            print(f"[JUDGE] Routing to verdict phase")
            return "verdict"
        
        # Check iteration count as failsafe for termination - IMPROVED LOGIC
        iteration = state.get("iteration_count", 0)
        if iteration >= 20:  # Force verdict at iteration 20 to ensure natural conclusion
            print(f"[JUDGE] Iteration {iteration} >= 20, forcing verdict for natural conclusion")
            return "verdict"
        
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
