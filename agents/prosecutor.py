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
        
        # Initialize citation enforcer for verification
        from core.enhanced_rag_system import CitationEnforcer, EnhancedHallucinationDetector
        self.citation_enforcer = CitationEnforcer()
        self.hallucination_detector = EnhancedHallucinationDetector()
        
        self.system_prompt = """
You are a professional prosecutor advocating for justice in a courtroom simulation. Your role is to present evidence-based arguments grounded in law and facts.

🚨 MANDATORY CITATION REQUIREMENT:
YOU MUST cite specific sources for EVERY legal claim you make. Use the format:
- [IPC-1], [CAS-2], etc. when referencing retrieved documents
- "According to IPC Section 499 [IPC-1]..."
- "In the case of X vs Y [CAS-3]..."
- "The evidence shows [DOC-2]..."

❌ ARGUMENTS WITHOUT CITATIONS WILL BE REJECTED ❌

CRITICAL: You have access to comprehensive structured legal context below. USE THIS CONTEXT to support EVERY argument. DO NOT make claims without citing the relevant source from the context.

ARGUMENT FLOW MANAGEMENT:
1. Review the COMPLETE conversation history and FULL retrieved legal context
2. NEVER repeat arguments already made - build upon them or introduce new counterpoints
3. Directly address and counter the defense lawyer's latest arguments
4. Maintain a logical progression: Case Overview → Evidence → Legal Application → Rebuttal → Conclusion
5. Track what has been discussed to avoid redundancy

ITERATION AWARENESS:
- Current iteration: {iteration}
- If iteration >= 15: Start preparing your CLOSING ARGUMENT
- If iteration >= 18: Deliver FINAL CLOSING STATEMENT and rest your case

ARGUMENT QUALITY:
- Present arguments as natural dialogue, not bullet points
- Be concise and impactful (3-5 key sentences per argument)
- ALWAYS cite sources: "According to IPC Section X [IPC-1]..."
- Focus on: (a) Evidence against the defendant (b) Applicable laws (c) Logical reasoning
- Maintain objectivity and professional tone

CLOSING SIGNALS:
When ready to conclude (iteration 18+), use phrases like:
- "In conclusion, Your Honor..."
- "Based on all the evidence and legal provisions discussed..."
- "The prosecution rests its case."
"""

    def get_thought_steps(self) -> List[str]:
        """Get prosecutor-specific chain of thought steps"""
        return [
            "1. REVIEW & STRATEGIZE: Carefully read the ENTIRE conversation history and the FULL retrieved legal context with all sections. Identify: (a) What arguments have YOU already made (b) What the defense lawyer claimed most recently (c) What the judge's feedback was. Check the current iteration number. If iteration >= 15, plan your closing argument. If iteration >= 18, prepare final closing statement.",
            "2. CONSTRUCT ARGUMENT WITH CITATIONS: Using the retrieved legal context, construct a persuasive argument as natural dialogue. MANDATORY: Cite sources using [IPC-1], [CAS-2] format for EVERY claim. Structure: (a) Direct rebuttal to defense's latest point WITH CITATION (b) Your main prosecutorial argument with legal support AND CITATION (c) Evidence presentation WITH CITATION (d) Conclusion. Be concise (3-5 sentences). If iteration >= 18, deliver your FINAL CLOSING STATEMENT with citations and indicate you rest your case."
        ]

    async def process(self, state: AgentState) -> AgentState:
        """Process current state with prosecutor-specific logic"""
        
        # Get iteration count and legal context
        iteration = state.get("iteration_count", 0)
        retrieved_context = state.get("retrieved_context", "")
        retrieved_docs = state.get("retrieved_docs", [])
        
        # Safety check: Ensure thought_step is within bounds
        thought_steps = self.get_thought_steps()
        current_step = state.get("thought_step", 0)
        
        if current_step >= len(thought_steps):
            print(f"[WARNING] Prosecutor thought_step {current_step} out of range (max {len(thought_steps)-1}), resetting to 0")
            current_step = 0
        
        # Add FULL legal context and iteration info to system prompt
        enhanced_prompt = self.system_prompt.format(iteration=iteration)
        if retrieved_context:
            # NO TRUNCATION - pass full context
            enhanced_prompt += f"\n\n{'='*80}\nRETRIEVED LEGAL CONTEXT (FULL):\n{'='*80}\n{retrieved_context}\n{'='*80}\n"
        else:
            enhanced_prompt += "\n\n⚠ WARNING: No legal context available. You MUST cite sources but none are available."
        
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
            result_content = "Prosecutor is analyzing the case and preparing arguments."
        
        # VERIFY CITATIONS AND HALLUCINATIONS (only for final argument, not during thinking)
        if state["thought_step"] == 1:  # Final argument step
            print(f"\n[PROSECUTOR] Verifying citations and hallucinations...")
            
            # Check citations
            citation_analysis = self.citation_enforcer.check_citations(result_content)
            print(f"[PROSECUTOR] Citations found: {citation_analysis['citation_count']} direct citations, {citation_analysis['legal_entity_count']} legal references")
            
            # Check hallucinations if we have context
            if retrieved_docs:
                hallucination_check = self.hallucination_detector.verify_claims(result_content, retrieved_docs)
                print(f"[PROSECUTOR] Hallucination check: {hallucination_check['verification_rate']} claims verified")
                if hallucination_check['warnings']:
                    for warning in hallucination_check['warnings']:
                        print(f"[PROSECUTOR] {warning}")
        
        # Simplified workflow - only 2 steps
        if state["thought_step"] == 0:
            response = {
                "messages": [HumanMessage(content=result_content, name="prosecutor")],
                "next": "self",
                "thought_step": state["thought_step"] + 1,
                "caller": "prosecutor",
                "iteration_count": iteration,
                "retrieved_context": retrieved_context,
                "retrieved_docs": retrieved_docs
            }
        elif state["thought_step"] == 1:
            response = {
                "messages": [HumanMessage(content=result_content, name="prosecutor")],
                "next": "judge",
                "thought_step": 0,
                "caller": "prosecutor",
                "iteration_count": iteration,
                "retrieved_context": retrieved_context,
                "retrieved_docs": retrieved_docs
            }
        else:
            raise ValueError("Invalid thought step")
            
        return response
