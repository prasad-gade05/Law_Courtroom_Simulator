from typing import Dict, Any, List, Optional, Literal, TypedDict
from langchain_core.messages import HumanMessage
from langchain.tools import BaseTool
from .base import AgentState, safe_get_content
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
You are a professional defense lawyer representing your client in a courtroom simulation. Your role is to present strong, fact-based arguments grounded in evidence and law.

CRITICAL: You have access to comprehensive legal context that was retrieved at the start of the trial. USE THIS CONTEXT to support your arguments. DO NOT request additional documents - focus on ARGUING your case.

ARGUMENT FLOW MANAGEMENT:
1. Review the COMPLETE conversation history and retrieved legal context
2. NEVER repeat arguments already made - build upon them or introduce new points
3. Reference and respond to the prosecutor's latest arguments
4. Maintain a logical progression: Introduction → Key Arguments → Supporting Evidence → Conclusion
5. Track what has been discussed and what remains to be addressed

ITERATION AWARENESS:
- Current iteration: {iteration}
- If iteration >= 15: Start preparing your CLOSING ARGUMENT
- If iteration >= 18: Deliver FINAL CLOSING STATEMENT and rest your case

ARGUMENT QUALITY:
- Present arguments as natural dialogue, not bullet points
- Be concise and impactful (3-5 key sentences per argument)
- Reference the legal context: "According to IPC Section X which was provided..."
- Focus on: (a) Facts from case files (b) Applicable laws (c) Logical reasoning
- Maintain professional tone while being persuasive

CLOSING SIGNALS:
When ready to conclude (iteration 18+), use phrases like:
- "In conclusion, Your Honor..."
- "Based on the evidence and legal precedents discussed..."
- "The defense rests."
"""

    def get_thought_steps(self) -> List[str]:
        """Get lawyer-specific chain of thought steps"""
        return [
            "1. REVIEW & STRATEGIZE: Carefully read the ENTIRE conversation history and the retrieved legal context. Identify: (a) What arguments have YOU already made (b) What the prosecutor claimed most recently (c) What the judge's feedback was. Check the current iteration number. If iteration >= 15, plan your closing argument. If iteration >= 18, prepare final closing statement.",
            "2. CONSTRUCT ARGUMENT: Using the retrieved legal context available in the conversation history, construct a persuasive argument as natural dialogue. Structure: (a) Direct response to prosecutor's latest point (b) Your main argument with legal support (c) Conclusion. Use phrases like 'According to IPC Section X...' to reference the legal context. Be concise (3-5 sentences). If iteration >= 18, deliver your FINAL CLOSING STATEMENT and indicate you rest your case."
        ]

    async def process(self, state: AgentState) -> AgentState:
        """Process current state with lawyer-specific logic"""
        
        # Get iteration count and legal context
        iteration = state.get("iteration_count", 0)
        retrieved_context = state.get("retrieved_context", "")
        
        # Safety check: Ensure thought_step is within bounds
        thought_steps = self.get_thought_steps()
        current_step = state.get("thought_step", 0)
        
        if current_step >= len(thought_steps):
            print(f"[WARNING] Lawyer thought_step {current_step} out of range (max {len(thought_steps)-1}), resetting to 0")
            current_step = 0
        
        # Add legal context and iteration info to system prompt
        enhanced_prompt = self.system_prompt.format(iteration=iteration)
        if retrieved_context:
            enhanced_prompt += f"\n\nRETRIEVED LEGAL CONTEXT:\n{retrieved_context[:2000]}\n...(context available)"
        
        messages = [
            {"role": "system", "content": enhanced_prompt + "\n'current_task': " + thought_steps[current_step]}
        ] + state["messages"]

        for i, llm in enumerate(self.llms):
            try:
                result = llm.invoke(messages)
                break
            except Exception as e:
                print(f"LLM {i} failed with error: {e}")
                continue
        
        # Safely extract content from result
        result_content = safe_get_content(result)
        
        # Ensure we have meaningful content
        if not result_content or len(result_content.strip()) < 10:
            result_content = "Defense counsel is analyzing the case and preparing arguments."
        
        # Simplified workflow - removed user_feedback to focus on arguing
        if state["thought_step"] == 0:
            response = {
                "messages": [HumanMessage(content=result_content, name="lawyer")],
                "next": "self",
                "thought_step": state["thought_step"] + 1,
                "caller": "lawyer",
                "iteration_count": iteration
            }
        elif state["thought_step"] == 1:
            response = {
                "messages": [HumanMessage(content=result_content, name="lawyer")],
                "next": "judge",
                "thought_step": 0,
                "caller": "lawyer",
                "iteration_count": iteration
            }
        else:
            raise ValueError("Invalid thought step")
        return response
