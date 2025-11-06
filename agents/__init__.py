"""Agent implementations for the Legal RAG system"""
from .base import AgentState
from .lawyer import LawyerAgent
from .prosecutor import ProsecutorAgent
from .judge import JudgeAgent
from .retriever import RetrieverAgent
from .initial_retriever import InitialRetrieverAgent
from .kanoon_fetcher import FetchingAgent
from .web_search import WebSearcherAgent
from .document_summarizer import DocumentSummarizationAgent

__all__ = [
    'AgentState',
    'LawyerAgent',
    'ProsecutorAgent',
    'JudgeAgent',
    'RetrieverAgent',
    'InitialRetrieverAgent',
    'FetchingAgent',
    'WebSearcherAgent',
    'DocumentSummarizationAgent'
]