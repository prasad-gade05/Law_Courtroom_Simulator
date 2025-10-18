from typing import Dict, Any, List, Optional, TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver
import os
import json

from agents import LawyerAgent, ProsecutorAgent, JudgeAgent, RetrieverAgent, FetchingAgent, WebSearcherAgent
from agents import AgentState

class TrialWorkflow:
    """
    Manages the trial workflow using LangGraph.
    Orchestrates interactions between different agents (judge, lawyer, prosecutor etc.)
    in a legal trial simulation.
    """
    
    def __init__(
        self,
        lawyer: LawyerAgent,
        prosecutor: ProsecutorAgent, 
        judge: JudgeAgent,
        retriever: RetrieverAgent,
        kanoon_fetcher: FetchingAgent,
        web_searcher: WebSearcherAgent
    ):
        """
        Initialize the trial workflow with required agents.
        
        Args:
            lawyer: Agent representing defense counsel
            prosecutor: Agent representing prosecution
            judge: Agent managing trial flow and making decisions
            retriever: Agent for retrieving relevant legal information
            kanoon_fetcher: Agent for fetching case-specific data
            web_searcher: Agent for web searches
        """
        self.lawyer = lawyer
        self.prosecutor = prosecutor
        self.judge = judge
        self.retriever = retriever
        self.kanoon_fetcher = kanoon_fetcher
        self.web_searcher = web_searcher
        self.memory = MemorySaver()  # For checkpointing workflow state
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """
        Create and configure the trial workflow graph.
        Defines nodes (agents) and edges (transitions) between them.
        """
        # Initialize graph with AgentState as state type
        workflow = StateGraph(AgentState)
        
        # Add agent nodes to graph
        workflow.add_node("kanoon_fetcher", self._kanoon_fetcher_node)
        workflow.add_node("judge", self._judge_node)
        workflow.add_node("lawyer", self._lawyer_node)
        workflow.add_node("prosecutor", self._prosecutor_node)
        workflow.add_node("retriever", self._retriever_node)
        workflow.add_node("web_searcher", self._web_search_node)
        workflow.add_node("user_feedback", self._user_feedback_node)
        
        # Define initial workflow path
        workflow.add_edge(START, "kanoon_fetcher")
        workflow.add_edge("kanoon_fetcher", "prosecutor")
        
        workflow.add_edge("user_feedback", "lawyer")
        
        # Judge's routing options
        workflow.add_conditional_edges(
            "judge",
            self._route_from_judge,
            {
                "lawyer": "lawyer",
                "prosecutor": "prosecutor", 
                "retriever": "retriever",
                "self": "judge",
                "web_searcher": "web_searcher",
                "END": END
            }
        )
        
        # Lawyer's routing options
        workflow.add_conditional_edges(
            "lawyer",
            self._route_from_agent,
            {
                "judge": "judge",
                "retriever": "retriever",
                "web_searcher": "web_searcher",
                "user_feedback": "user_feedback",
                "self": "lawyer"  # For chain of thought reasoning
            }
        )
        
        # Prosecutor's routing options
        workflow.add_conditional_edges(
            "prosecutor",
            self._route_from_agent,
            {
                "judge": "judge",
                "retriever": "retriever",
                "web_searcher": "web_searcher",
                "self": "prosecutor"  # For chain of thought reasoning
            }
        )
        
        # Retriever routes back to calling agent
        workflow.add_conditional_edges(
            "retriever",
            self._route_from_retriever,
            {
                "lawyer": "lawyer",
                "prosecutor": "prosecutor",
                "judge": "judge"
            }
        )

        # Web searcher routes back to calling agent
        workflow.add_conditional_edges(
            "web_searcher",
            self._route_from_retriever,
            {
                "judge": "judge",
                "lawyer": "lawyer",
                "prosecutor": "prosecutor"
            }
        )
        
        return workflow.compile(checkpointer=self.memory, interrupt_before=["user_feedback"])
    
    # Agent node processing methods
    async def _kanoon_fetcher_node(self, state: AgentState) -> AgentState:
        """Kanoon Fetcher node processing"""
        return await self.kanoon_fetcher.process(state)
    
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
    
    async def _user_feedback_node(self, state: AgentState) -> AgentState:
        """User feedback node processing"""
        # print(f"User feedback node processing with state: {state}")
        pass
    
    # Routing logic methods
    def _route_from_judge(self, state: AgentState) -> str:
        """Determine next agent based on judge's decision"""
        return state["next"]
    
    def _route_from_agent(self, state: AgentState) -> str:
        """Determine next step from lawyer or prosecutor actions"""
        return state["next"]
    
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
            )

            print(f"Initial state created")
            print(f"  Starting node: kanoon_fetcher")
            print(f"  Thought step: 0")
            print(f"  Message count: {len(initial_state['messages'])}")

            thread = {"configurable": {"thread_id": "1"}}

            yield {
                "status": "progress",
                "content": "Workflow initialized, starting execution...",
            }

            # Stream workflow states
            try:
                iteration_count = 0
                max_iterations = 50
                
                print(f"\nStarting workflow stream (max {max_iterations} iterations)")
                print("-"*80)
                
                async for state in self.graph.astream(initial_state, thread, stream_mode="updates"):
                    iteration_start = time.time()
                    iteration_count += 1
                    
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
                        print(f"  Next node: {next_node}")
                        print(f"  Messages in state: {message_count}")
                    
                    # Yield progress
                    yield {
                        "status": "progress",
                        "content": f"Agent '{node_name}' completed",
                        "data": f"Iteration {iteration_count}, Next: {next_node if isinstance(node_output, dict) else 'unknown'}"
                    }
                    
                    iteration_time = time.time() - iteration_start
                    print(f"  Duration: {iteration_time:.2f}s")
                    
                    # Check for END condition
                    if isinstance(node_output, dict):
                        next_node = node_output.get("next")
                        if next_node == "END":
                            print(f"\n[WORKFLOW END] Reached END state at iteration {iteration_count}")
                            print(f"Total time: {time.time() - workflow_start_time:.1f}s")
                            yield {"status": "done", "content": "Workflow completed with verdict"}
                            return
                        
                        # Check if we're at user_feedback (interrupt point)
                        if next_node == "user_feedback":
                            print(f"\n[USER FEEDBACK] Checkpoint reached at iteration {iteration_count}")
                            feedback_message = "Please strengthen the arguments with more legal precedents."
                            
                            print(f"  Providing automatic feedback: {feedback_message[:80]}...")
                            
                            # Update state with feedback
                            self.graph.update_state(
                                thread,
                                {"messages": [HumanMessage(content=feedback_message, name="user")]},
                                as_node="user_feedback"
                            )
                            
                            print(f"  Resuming workflow after feedback...")
                            
                            # Continue streaming
                            async for resume_state in self.graph.astream(None, thread, stream_mode="updates"):
                                resume_start = time.time()
                                iteration_count += 1
                                
                                print(f"\n[ITERATION {iteration_count}] Started (post-feedback)")
                                print(f"  Time elapsed: {time.time() - workflow_start_time:.1f}s")
                                
                                if not resume_state:
                                    print("  WARNING: Empty resume state, skipping...")
                                    continue
                                    
                                resume_node = list(resume_state.keys())[0]
                                resume_output = resume_state.get(resume_node, {})
                                
                                print(f"  Node: {resume_node}")
                                
                                if isinstance(resume_output, dict):
                                    resume_next = resume_output.get("next", "unknown")
                                    print(f"  Next node: {resume_next}")
                                
                                yield {
                                    "status": "progress",
                                    "content": f"Agent '{resume_node}' completed",
                                    "data": f"Iteration {iteration_count}, Post-feedback"
                                }
                                
                                resume_time = time.time() - resume_start
                                print(f"  Duration: {resume_time:.2f}s")
                                
                                if isinstance(resume_output, dict) and resume_output.get("next") == "END":
                                    print(f"\n[WORKFLOW END] Reached END state at iteration {iteration_count}")
                                    print(f"Total time: {time.time() - workflow_start_time:.1f}s")
                                    yield {"status": "done", "content": "Workflow completed with verdict"}
                                    return
                                
                                if iteration_count >= max_iterations:
                                    print(f"\n[MAX ITERATIONS] Reached limit of {max_iterations}")
                                    print(f"Total time: {time.time() - workflow_start_time:.1f}s")
                                    yield {"status": "done", "content": "Workflow completed (max iterations reached)"}
                                    return
                    
                    # Safety check for max iterations
                    if iteration_count >= max_iterations:
                        print(f"\n[MAX ITERATIONS] Reached limit of {max_iterations}")
                        print(f"Total time: {time.time() - workflow_start_time:.1f}s")
                        yield {"status": "done", "content": "Workflow completed (max iterations reached)"}
                        return
                            
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

