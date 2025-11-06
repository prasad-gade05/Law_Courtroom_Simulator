from typing import Dict, Any, List, Optional, TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver
import os
import json
import time

from agents.base import AgentState
from agents.judge import JudgeAgent
from agents.verdict_agent import VerdictAgent

class TrialWorkflow:
    """
    Manages the trial workflow using LangGraph.
    Orchestrates interactions between different agents (judge, lawyer, prosecutor etc.)
    in a legal trial simulation.
    """
    
    def __init__(
        self,
        lawyer,
        prosecutor, 
        judge,
        retriever,
        initial_retriever,  # NEW: Initial retriever for comprehensive document fetch
        kanoon_fetcher,
        web_searcher,
        document_summarizer,
        llms
    ):
        """
        Initialize the trial workflow with required agents.
        
        Args:
            lawyer: Agent representing defense counsel
            prosecutor: Agent representing prosecution
            judge: Agent managing trial flow and making decisions
            retriever: Agent for retrieving relevant legal information (legacy, kept for compatibility)
            initial_retriever: Agent for initial comprehensive document retrieval
            kanoon_fetcher: Agent for fetching case-specific data
            web_searcher: Agent for web searches
            document_summarizer: Agent for summarizing fetched documents
        """
        self.lawyer = lawyer
        self.prosecutor = prosecutor
        self.judge = judge
        self.retriever = retriever
        self.initial_retriever = initial_retriever  # NEW
        self.kanoon_fetcher = kanoon_fetcher
        self.web_searcher = web_searcher
        self.document_summarizer = document_summarizer
        self.verdict_agent = VerdictAgent(llms)
        self.memory = MemorySaver()
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create and configure the trial workflow graph with initial retrieval phase"""
        workflow = StateGraph(AgentState)
        
        # 1. Add all nodes
        workflow.add_node("kanoon_fetcher", self._kanoon_fetcher_node)
        workflow.add_node("document_summarizer", self._document_summarizer_node)
        workflow.add_node("initial_retriever", self._initial_retriever_node)  # NEW
        workflow.add_node("judge", self._judge_node)
        workflow.add_node("lawyer", self._lawyer_node)
        workflow.add_node("prosecutor", self._prosecutor_node)
        workflow.add_node("verdict", self._verdict_node)

        # 2. Define the workflow path - START with comprehensive document retrieval
        workflow.set_entry_point("kanoon_fetcher")
        workflow.add_edge("kanoon_fetcher", "document_summarizer")
        workflow.add_edge("document_summarizer", "initial_retriever")  # NEW: Fetch all docs first
        workflow.add_edge("initial_retriever", "prosecutor")  # Then proceed to opening statements
        
        # 3. Simplified routing - NO retriever/web_searcher calls during debate
        workflow.add_conditional_edges(
            "lawyer",
            self._route_from_lawyer_or_prosecutor,
            {
                "continue_debate": "judge",
                "end_debate": "verdict",
                "self": "lawyer"
            }
        )
        workflow.add_conditional_edges(
            "prosecutor",
            self._route_from_lawyer_or_prosecutor,
            {
                "continue_debate": "judge",
                "end_debate": "verdict",
                "self": "prosecutor"
            }
        )
        
        # 4. The Judge moderates the debate
        workflow.add_conditional_edges(
            "judge",
            self._route_from_judge,
            {
                "lawyer": "lawyer",
                "prosecutor": "prosecutor",
                "verdict": "verdict",
                "self": "judge",
                "END": END
            }
        )
        
        # 5. The verdict node is the final step
        workflow.add_edge("verdict", END)
        
        # 6. Compile the graph without user_feedback interruption
        return workflow.compile(checkpointer=self.memory)
    
    # Agent node processing methods
    async def _kanoon_fetcher_node(self, state: AgentState) -> AgentState:
        """Kanoon Fetcher node processing"""
        return await self.kanoon_fetcher.process(state)
    
    async def _document_summarizer_node(self, state: AgentState) -> AgentState:
        """Document Summarizer node processing"""
        print("\n[WORKFLOW] Document summarizer activated - processing fetched documents")
        result = await self.document_summarizer.process(state)
        
        # After summarization, we need to trigger vector database re-indexing
        # by deleting the chroma_db cache
        print("[WORKFLOW] Triggering vector database re-indexing...")
        try:
            import shutil
            chroma_path = "chroma_db/public"
            if os.path.exists(chroma_path):
                shutil.rmtree(chroma_path)
                print(f"[WORKFLOW] Deleted {chroma_path} - will re-index with summaries on next retrieval")
        except Exception as e:
            print(f"[WORKFLOW] Could not delete chroma cache: {e}")
        
        return result
    
    async def _initial_retriever_node(self, state: AgentState) -> AgentState:
        """Initial comprehensive retrieval node processing"""
        print("\n[WORKFLOW] Initial retriever activated - fetching all relevant documents")
        return await self.initial_retriever.process(state)
    
    async def _judge_node(self, state: AgentState) -> AgentState:
        """Judge node processing"""
        # print(f"Judge node processing with state: {state}")
        return await self.judge.process(state)
    
    async def _lawyer_node(self, state: AgentState) -> AgentState:
        """Lawyer node processing"""
        # print(f"Lawyer node processing with state: {state}")
        return await self.lawyer.process(state)
    
    async def _prosecutor_node(self, state: AgentState) -> AgentState:
        """Prosecutor node processing"""
        # print(f"Prosecutor node processing with state: {state}")
        return await self.prosecutor.process(state)
    
    async def _retriever_node(self, state: AgentState) -> AgentState:
        """Retriever node processing"""
        # print(f"Retriever node processing with state: {state}")
        return await self.retriever.process(state)
    
    async def _web_search_node(self, state: AgentState) -> AgentState:
        """Web Search node processing"""
        # print(f"Web Search node processing with state: {state}")
        return await self.web_searcher.process(state)
    
    async def _verdict_node(self, state: AgentState) -> AgentState:
        """This node calls our VerdictAgent to deliver the final judgment."""
        print("\n[VERDICT NODE] Processing verdict...")
        verdict_result = await self.verdict_agent.process(state)
        
        # Ensure we properly merge the verdict result with existing state
        updated_state = {
            **state,  # Preserve existing state fields
            **verdict_result  # Override with verdict results
        }
        
        print(f"[VERDICT NODE] Verdict returned: next={verdict_result.get('next', 'unknown')}")
        return updated_state
    
    # Routing logic methods
    def _route_from_judge(self, state: AgentState) -> str:
        """Determine next agent based on judge's decision"""
        return state["next"]
    
    def should_end_debate(self, state: AgentState) -> Literal["continue_debate", "end_debate"]:
        """Determine when the debate should end naturally by iteration 20"""
        iteration_count = state.get("iteration_count", 0)
        messages = state.get("messages", [])
        
        # Natural verdict by iteration 20
        MAX_DEBATE_ITERATIONS = 20

        # Check for natural ending keywords
        last_message_content = messages[-1].content.lower() if messages and hasattr(messages[-1], 'content') else ""
        end_keywords = ["i rest my case", "the prosecution rests", "the defense rests", "no further arguments", "we await the court's decision", "in conclusion, your honor"]

        if any(keyword in last_message_content for keyword in end_keywords):
            print(f"[ROUTER] End keyword detected in iteration {iteration_count}. Proceeding to verdict.")
            return "end_debate"

        # Progressive natural ending based on iteration count
        if iteration_count >= MAX_DEBATE_ITERATIONS:
            print(f"[ROUTER] Iteration {iteration_count} reached max of {MAX_DEBATE_ITERATIONS}. Forcing verdict.")
            return "end_debate"
        elif iteration_count >= 18:
            print(f"[ROUTER] Iteration {iteration_count} >= 18. Strongly encouraging conclusion.")
            # At this point, agents should be delivering closing statements
            return "end_debate"
        elif iteration_count >= 15:
            print(f"[ROUTER] Iteration {iteration_count} >= 15. Starting to wind down debate.")
            # Agents will start preparing closing arguments
            return "continue_debate"
        else:
            print(f"[ROUTER] Continuing debate. Current iteration: {iteration_count}")
            return "continue_debate"
    
    
    def _route_from_agent(self, state: AgentState) -> str:
        """Determine next step from lawyer or prosecutor actions"""
        return state["next"]
    
    def _route_from_lawyer_or_prosecutor(self, state: AgentState) -> str:
        """
        Enhanced routing logic for lawyer and prosecutor that can route to verdict
        or continue the debate based on intelligent analysis.
        """
        # First check the agent's intended next action
        intended_next = state.get("next", "judge")
        
        # If the agent wants to go to self (multi-step thought process), honor that
        if intended_next == "self":
            return "self"
        
        # If the agent intends to go to judge (normal debate flow), check if debate should end
        if intended_next == "judge":
            return self.should_end_debate(state)
        
        # Default to continue debate for normal flow
        return "continue_debate"
    
    def _route_from_retriever(self, state: AgentState) -> str:
        """Route back to the agent that called the retriever"""
        return state["next"]
    
    async def run(self, user_prompt: str):
        """
        Run the trial workflow as an async generator.
        Streams all workflow states until completion.
        
        Args:
            user_prompt: Initial prompt to start the trial
        """
        import time
        workflow_start_time = time.time()
        
        print("\n" + "="*80)
        print("WORKFLOW EXECUTION STARTED")
        print("="*80)
        
        try:
            # Set up initial state
            initial_state = AgentState(
                messages=[HumanMessage(content=user_prompt)],
                next="kanoon_fetcher",
                thought_step=0,
                iteration_count=0,  # NEW: Initialize iteration counter
                web_search_count=0,  # NEW: Initialize web search counter
            )

            print(f"Initial state created")
            print(f"  Starting node: kanoon_fetcher")
            print(f"  Thought step: 0")
            print(f"  Message count: {len(initial_state['messages'])}")

            thread = {"configurable": {"thread_id": "1", "recursion_limit": 40}}  # Further increased to 40 to ensure verdict is reached

            yield {
                "status": "progress",
                "content": "Workflow initialized, starting execution...",
            }

            # Stream workflow states
            try:
                iteration_count = 0
                max_iterations = 25  # Set to 25 to match LangGraph's default limit
                yielded_events = set()  # NEW: Track yielded events to prevent duplicates
                
                print(f"\nStarting workflow stream (max {max_iterations} iterations)")
                print("-"*80)
                
                async for state in self.graph.astream(initial_state, thread, stream_mode="updates"):
                    iteration_start = time.time()
                    iteration_count += 1
                    
                    # SAFETY: Force verdict if we're approaching recursion limit
                    if iteration_count >= 22:
                        print(f"\n[SAFETY] Iteration {iteration_count} >= 22, forcing immediate verdict")
                        # Get the current state and generate verdict directly
                        current_state = initial_state if iteration_count == 1 else state
                        final_state_copy = None
                        for node_name, node_state in state.items():
                            if isinstance(node_state, dict):
                                final_state_copy = node_state
                                break
                        
                        if final_state_copy:
                            try:
                                verdict_result = await self.verdict_agent.process(final_state_copy)
                                verdict_msg_content = ""
                                if verdict_result.get("messages"):
                                    latest_msg = verdict_result["messages"][-1]
                                    verdict_msg_content = latest_msg.content if hasattr(latest_msg, 'content') else str(latest_msg)
                                
                                if verdict_msg_content:
                                    yield {
                                        "status": "progress",
                                        "agent_name": "verdict",
                                        "iteration": iteration_count,
                                        "next_agent": "END",
                                        "agent_message": verdict_msg_content,
                                        "content": "Emergency verdict (preventing recursion limit)"
                                    }
                            except Exception as e:
                                print(f"[ERROR] Emergency verdict failed: {e}")
                        
                        # Yield final done status
                        yield {
                            "status": "done",
                            "agent_name": "verdict",
                            "iteration": iteration_count,
                            "agent_message": "VERDICT DELIVERED: The court has concluded deliberations.",
                            "content": "Workflow completed with emergency verdict"
                        }
                        return
                    
                    print(f"\n[ITERATION {iteration_count}] Started")
                    print(f"  Time elapsed: {time.time() - workflow_start_time:.1f}s")
                    
                    # Check if state is None or empty
                    if state is None or not state:
                        print("  WARNING: Received empty state, skipping...")
                        continue
                    
                    # Extract node name and output
                    node_name = list(state.keys())[0] if state else "unknown"
                    node_output = state.get(node_name, {})
                    
                    print(f"  Node: {node_name}")
                    
                    if isinstance(node_output, dict):
                        next_node = node_output.get("next", "unknown")
                        message_count = len(node_output.get("messages", []))
                        current_iteration = node_output.get("iteration_count", iteration_count)
                        print(f"  Next node: {next_node}")
                        print(f"  Messages in state: {message_count}")
                        
                        # Update state iteration count
                        node_output["iteration_count"] = iteration_count
                    
                    # Extract agent message content for display
                    agent_message = ""
                    if isinstance(node_output, dict) and node_output.get("messages"):
                        messages_list = node_output.get("messages", [])
                        if messages_list and len(messages_list) > 0:
                            latest_msg = messages_list[-1]
                            # Extract content from the message object
                            if hasattr(latest_msg, 'content'):
                                agent_message = latest_msg.content
                            elif isinstance(latest_msg, dict) and 'content' in latest_msg:
                                agent_message = latest_msg['content']
                            elif isinstance(latest_msg, str):
                                agent_message = latest_msg
                    
                    # Ensure agent_message is a string
                    if not isinstance(agent_message, str):
                        agent_message = str(agent_message) if agent_message else ""
                    
                    # Check for verdict in message content
                    verdict_delivered = "VERDICT DELIVERED" in agent_message or "Given Verdict" in agent_message
                    
                    # Create unique event key to prevent duplicates
                    event_key = f"{iteration_count}_{node_name}_{next_node if isinstance(node_output, dict) else 'unknown'}"
                    
                    # Yield progress only if not duplicate
                    if event_key not in yielded_events:
                        yield {
                            "status": "progress",
                            "agent_name": node_name,
                            "iteration": iteration_count,
                            "next_agent": next_node if isinstance(node_output, dict) else "unknown",
                            "agent_message": agent_message,  # NEW: Include actual message
                            "content": f"Agent '{node_name}' completed"
                        }
                        yielded_events.add(event_key)
                    
                    iteration_time = time.time() - iteration_start
                    print(f"  Duration: {iteration_time:.2f}s")
                    
                    # Check for END condition or verdict delivery
                    if isinstance(node_output, dict):
                        next_node = node_output.get("next")
                        
                        # Let the graph manage its own flow - removed manual routing logic
                        # The graph's conditional edges will handle verdict routing naturally
                        
                        # Handle verdict node - extract and yield the verdict message
                        if node_name == "verdict":
                            print(f"\n[VERDICT NODE] Verdict phase triggered at iteration {iteration_count}")
                            # Extract verdict from the node output
                            verdict_message = ""
                            if isinstance(node_output, dict) and node_output.get("messages"):
                                verdict_msgs = node_output.get("messages", [])
                                if verdict_msgs and len(verdict_msgs) > 0:
                                    latest_msg = verdict_msgs[-1]
                                    if hasattr(latest_msg, 'content'):
                                        verdict_message = latest_msg.content
                                    elif isinstance(latest_msg, dict) and 'content' in latest_msg:
                                        verdict_message = latest_msg['content']
                            
                            # If we got verdict message from current iteration
                            if not verdict_message and agent_message:
                                verdict_message = agent_message
                            
                            print(f"[VERDICT NODE] Verdict message extracted (length: {len(verdict_message)})")
                            
                            # Yield the verdict immediately
                            if verdict_message and len(verdict_message.strip()) > 0:
                                verdict_event_key = f"verdict_{iteration_count}"
                                if verdict_event_key not in yielded_events:
                                    yield {
                                        "status": "progress",
                                        "agent_name": "verdict",
                                        "iteration": iteration_count,
                                        "next_agent": "END",
                                        "agent_message": verdict_message,
                                        "content": "Final verdict rendered"
                                    }
                                    yielded_events.add(verdict_event_key)
                                    print(f"[VERDICT NODE] Verdict yielded to client")
                        elif next_node == "verdict":
                            print(f"\n[ROUTING] Routing to verdict node at iteration {iteration_count}")
                        
                        if next_node == "END":
                            print(f"\n[WORKFLOW END] Reached END state at iteration {iteration_count}")
                            print(f"Total time: {time.time() - workflow_start_time:.1f}s")
                            
                            # Try to extract verdict from messages if not already captured
                            verdict_found = False
                            final_verdict = ""
                            
                            if isinstance(node_output, dict) and node_output.get("messages"):
                                # Check all messages for verdict
                                for msg in reversed(node_output.get("messages", [])):
                                    msg_content = ""
                                    if hasattr(msg, 'content'):
                                        msg_content = msg.content
                                    elif isinstance(msg, dict) and 'content' in msg:
                                        msg_content = msg['content']
                                    
                                    if msg_content and ("verdict" in str(msg).lower() or "VERDICT DELIVERED" in msg_content.upper() or 
                                                       "GUILTY" in msg_content.upper() or "NOT GUILTY" in msg_content.upper()):
                                        final_verdict = msg_content
                                        verdict_found = True
                                        print(f"[WORKFLOW END] Verdict found in messages")
                                        break
                            
                            if not verdict_found:
                                final_verdict = agent_message if agent_message else "Verdict delivered"
                            
                            # Final yield to signal completion
                            yield {
                                "status": "done",
                                "agent_name": "verdict" if verdict_found else "judge",
                                "iteration": iteration_count,
                                "agent_message": final_verdict,
                                "content": "Workflow completed with verdict"
                            }
                            return
                    
                    # Removed manual max iteration check - let the graph manage its own lifecycle
                            
            except Exception as e:
                print(f"\n[ERROR] Workflow stream exception")
                print(f"  Error type: {type(e).__name__}")
                print(f"  Error message: {str(e)}")
                import traceback
                traceback.print_exc()
                yield {
                    "status": "error",
                    "content": f"Workflow error: {str(e)}"
                }
                return

            # If we reach here without END, workflow completed normally
            print(f"\n[WORKFLOW END] Stream ended naturally")
            print(f"Total time: {time.time() - workflow_start_time:.1f}s")
            print(f"Total iterations: {iteration_count}")
            yield {"status": "done", "content": "Workflow completed successfully"}
            
        except Exception as e:
            print(f"\n[FATAL ERROR] Workflow exception")
            print(f"  Error type: {type(e).__name__}")
            print(f"  Error message: {str(e)}")
            import traceback
            traceback.print_exc()
            yield {
                "status": "error",
                "content": f"Fatal workflow error: {str(e)}"
            }
    
    def visualize(self):
        """
        Generate and save visualization of the workflow graph.
        Outputs a PNG file showing the graph structure.
        """
        png_graph = self.graph.get_graph().draw_mermaid_png()
        with open("my_graph.png", "wb") as f:
            f.write(png_graph)

        print(f"Graph saved as 'my_graph.png' in {os.getcwd()}")

