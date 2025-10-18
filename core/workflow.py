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
        Handles the main execution loop including user feedback.
        
        Args:
            user_prompt: Initial prompt to start the trial
        """
        # Set up initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=user_prompt)],
            next="kanoon_fetcher",
            thought_step=0,
        )

        print(f"Initial state: {initial_state}")

        thread = {"configurable": {"thread_id": "1"}}

        yield {
            "status": "progress",
            "content": "Initializing workflow...",
        }

        # Stream initial workflow states
        async for state in self.graph.astream(initial_state, thread):
            print(state)
            print("-" * 100)
            yield {
                "status": "progress",
                "content": repr(state)
            }

        # Simulate user feedback loop
        user_input = "argument is not strong"

        while True:
            # Process user feedback
            self.graph.update_state(values={"user_feedback": user_input}, as_node="user_feedback")

            async for state in self.graph.astream(None, thread):
                print(state)
                print("-" * 100)
                yield {
                    "status": "progress",
                    "content": repr(state)
                }
                
            # Check for workflow completion
            try:
                if state.judge.next == 'END':
                    yield {"status": "done", "content": "Workflow completed successfully"}
                    break
            except AttributeError:
                pass
        
        # Run the workflow
        # final_state = await self.graph.ainvoke(initial_state)
        
        # Extract results
        # return {
        #     "messages": final_state["messages"],
        #     "verdict": next(
        #         (msg for msg in reversed(final_state["messages"]) 
        #          if hasattr(msg, "name") and msg.name == "judge"),
        #         None
        #     )
        # }
    
    def visualize(self):
        """
        Generate and save visualization of the workflow graph.
        Outputs a PNG file showing the graph structure.
        """
        png_graph = self.graph.get_graph().draw_mermaid_png()
        with open("my_graph.png", "wb") as f:
            f.write(png_graph)

        print(f"Graph saved as 'my_graph.png' in {os.getcwd()}")

