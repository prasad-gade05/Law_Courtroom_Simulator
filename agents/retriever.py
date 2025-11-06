from typing import Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from core.chroma_store import ChromaVectorStore
from core.advanced_rag import RetrievalAugmentor
from .base import AgentState, safe_get_content
from langchain_core.messages.utils import get_buffer_string
import os
from dotenv import load_dotenv
load_dotenv()
import re


def create_law_retriever(private=False):
    """Create ChromaDB vector store with advanced RAG capabilities"""
    if private:
        vector_store = ChromaVectorStore('private', './private_documents')
    else:
        vector_store = ChromaVectorStore('public', './public_documents')

    # Get base retriever from vector store
    base_retriever = vector_store.as_retriever()
    
    # Try to get documents for hybrid retrieval
    try:
        # Get all documents from the vector store for BM25 indexing
        all_docs = vector_store.vectorstore.get()
        if all_docs and 'documents' in all_docs:
            from langchain_core.documents import Document
            documents = [
                Document(page_content=text, metadata=meta) 
                for text, meta in zip(all_docs['documents'], all_docs['metadatas'])
            ]
        else:
            documents = []
    except Exception as e:
        print(f"[WARNING] Could not get documents for BM25: {e}")
        documents = []
    
    # Create advanced RAG retriever with re-ranking and compression
    augmentor = RetrievalAugmentor(base_retriever, documents)
    
    return augmentor
   
# class RetrieverResponse(BaseModel):
#     """Structured retriever response"""
#     # response: str = Field(description="The retriever's assessment of the retrieved content")
#     is_enough: bool = Field(description="Whether the retrieved content is enough to answer the request")

# class Queries(BaseModel):
#     private_query: str = Field(description="Query for private retriever (user case files or documents). 'none' if not needed")  
#     public_query: str = Field(description="Query for public retriever (public docs like IPC, legal case precedents, etc) 'none' if not needed")
class RetrieverAgent:
    """Agent for retrieving and analyzing legal documents from vector store"""
    
    def __init__(
        self,
        llms,
        # **kwargs
    ):
        self.private_retriever = create_law_retriever(private=True)
        self.public_retriever = create_law_retriever(private=False)
        self.llms = llms
        self.system_prompt = """
You are a legal research assistant specializing in retrieving and verifying relevant legal provisions, case laws, and statutes from the Indian Penal Code (IPC) and related legal documents.

CRITICAL RESPONSIBILITIES:
1. Formulate precise, specific queries based on inputs from the judge, lawyer, or prosecutor
2. Retrieve relevant documents using hybrid search (semantic + keyword matching)
3. VERIFY retrieved content for accuracy and relevance
4. DETECT potential hallucinations or unsupported claims
5. Provide ONLY verified, grounded information with proper citations

HALLUCINATION PREVENTION:
- Always include source document names with retrieved information
- If uncertain about a fact, explicitly state "This information needs verification"
- Never fabricate legal citations or case precedents
- If information is not found in the database, clearly state "Not found in available documents"

QUERY FORMULATION RULES:
- For IPC sections: Use specific section numbers (e.g., "IPC Section 302")
- For case law: Use party names or key legal principles
- For general concepts: Use precise legal terminology

OUTPUT FORMAT:
Always structure your response as:
1. Query used: [Your search query]
2. Retrieved information: [Exact excerpts from documents]
3. Source: [Document name and chunk reference]
4. Confidence: [High/Medium/Low based on relevance]

You have access to:
- private_retriever: User case files and private documents
- public_retriever: IPC, legal precedents, public legal documents

IMPORTANT: Be concise. Focus on accuracy over volume. Quality over quantity.
"""

    def get_thought_steps(self) -> List[str]:
        """Get retriever-specific chain of thought steps"""
        return [
            "1. Analyze the information request: Extract key legal concepts, specific section numbers, case names, or legal principles being requested. Note: Be specific and precise.",
            "2. Formulate PRIVATE query: If the request relates to user's case files or private documents, create a specific query. Include key terms from the request. If not needed, respond with exactly 'none'.",
            "3. Formulate PUBLIC query: If the request relates to IPC sections, case precedents, or public legal documents, create a specific query. Include section numbers or case names if mentioned. If not needed, respond with exactly 'none'.",
            "4. Assess retrieved documents: Review the retrieved content. Check if it directly answers the request. Verify that citations and references are present in the retrieved text. Assess confidence (High/Medium/Low). If low confidence or insufficient, note what's missing.",
            "5. Provide verified response: Extract and provide ONLY information that is explicitly present in the retrieved documents. Include: (a) Query used (b) Exact excerpts with quotation marks (c) Source filename (d) Confidence level. If no relevant information found, state clearly: 'No relevant information found in database for [specific topic].' Do NOT fabricate or extrapolate beyond what's in the documents."
        ]

    async def process(self, state: AgentState) -> AgentState:
        """Process current state with advanced RAG and hallucination detection"""
        
        try:
            messages = [
                {"role": "system", "content": self.system_prompt + f"\n'current_task': {self.get_thought_steps()[0]}"}
            ] + state["messages"]

            # Step 1: Analyze the request
            info_analysis = None
            for i, llm in enumerate(self.llms):
                try:
                    info_analysis = llm.invoke(messages)
                    break
                except Exception as e:
                    print(f"LLM {i} failed with error: {e}")
                    continue
            
            if info_analysis is None:
                return self._create_error_response(state, "Failed to analyze request")

            # Step 2 & 3: Formulate queries with improved prompting
            info_analysis_content = safe_get_content(info_analysis)
            
            # Step 2: Private query
            messages.append({"role": "assistant", "content": info_analysis_content})
            messages.append({"role": "system", "content": "current_task: " + self.get_thought_steps()[1]})
            
            private_query = None
            for i, llm in enumerate(self.llms):
                try:
                    private_query = llm.invoke(messages)
                    break
                except Exception as e:
                    print(f"LLM {i} failed with error: {e}")
                    continue

            if private_query is None:
                return self._create_error_response(state, "Failed to formulate private query")
            
            private_query_content = safe_get_content(private_query)
            messages.append({"role": "assistant", "content": private_query_content})
            
            # Step 3: Public query
            messages.append({"role": "system", "content": "current_task: " + self.get_thought_steps()[2]})
            
            public_query = None
            for i, llm in enumerate(self.llms):
                try:
                    public_query = llm.invoke(messages)
                    break
                except Exception as e:
                    print(f"LLM {i} failed with error: {e}")
                    continue

            if public_query is None:
                return self._create_error_response(state, "Failed to formulate public query")

            # Step 4: Retrieve with advanced RAG
            public_query_content = safe_get_content(public_query)
            
            private_retrieved_docs = []
            private_retrieved_content = "None"
            public_retrieved_docs = []
            public_retrieved_content = "None"
            
            # Use advanced RAG retrieval with re-ranking and compression
            try:
                if private_query_content.lower().strip() not in ['none', '']:
                    print(f"[RETRIEVER] Private query: {private_query_content[:100]}...")
                    private_retrieved_docs, private_meta = self.private_retriever.retrieve_and_compress(
                        private_query_content, k=10, top_k_compressed=5
                    )
                    private_retrieved_content = self.private_retriever.format_context_for_prompt(
                        private_retrieved_docs, include_metadata=True
                    )
                    print(f"[RETRIEVER] Private: Retrieved {private_meta['retrieved_count']}, compressed to {private_meta['compressed_count']}")
            except Exception as e:
                print(f"[ERROR] Private retriever failed: {e}")
                private_retrieved_content = "Error retrieving private documents"
            
            try:
                if public_query_content.lower().strip() not in ['none', '']:
                    print(f"[RETRIEVER] Public query: {public_query_content[:100]}...")
                    public_retrieved_docs, public_meta = self.public_retriever.retrieve_and_compress(
                        public_query_content, k=10, top_k_compressed=5
                    )
                    public_retrieved_content = self.public_retriever.format_context_for_prompt(
                        public_retrieved_docs, include_metadata=True
                    )
                    print(f"[RETRIEVER] Public: Retrieved {public_meta['retrieved_count']}, compressed to {public_meta['compressed_count']}")
            except Exception as e:
                print(f"[ERROR] Public retriever failed: {e}")
                public_retrieved_content = "Error retrieving public documents"

            # Step 5: Assess results with retrieved context
            messages.append({"role": "assistant", "content": public_query_content})
            messages.append({"role": "system", "content": f"""Retrieved Information:

PRIVATE DOCUMENTS:
{private_retrieved_content}

PUBLIC DOCUMENTS:
{public_retrieved_content}

current_task: {self.get_thought_steps()[3]}"""})
            
            assessment = None
            for i, llm in enumerate(self.llms):
                try:
                    assessment = llm.invoke(messages)
                    break
                except Exception as e:
                    print(f"LLM {i} failed with error: {e}")
                    continue

            if assessment is None:
                return self._create_error_response(state, "Failed to assess results")

            assessment_content = safe_get_content(assessment)
            messages.append({"role": "assistant", "content": assessment_content})

            # Step 6: Generate final verified response
            messages.append({"role": "system", "content": f"""current_task: {self.get_thought_steps()[4]}

REMINDER: Only provide information that is explicitly present in the retrieved documents above. Include exact quotes and sources."""})
            
            result = None
            for i, llm in enumerate(self.llms):
                try:
                    result = llm.invoke(messages)
                    break
                except Exception as e:
                    print(f"LLM {i} failed with error: {e}")
                    continue

            if result is None:
                return self._create_error_response(state, "Failed to generate final response")

            result_content = safe_get_content(result)
            
            # Verify response for hallucinations
            all_docs = private_retrieved_docs + public_retrieved_docs
            if all_docs:
                verification = self.private_retriever.verify_response(result_content, all_docs)
                
                # Add warning if low confidence
                if verification['confidence'] < 0.7 and verification['warnings']:
                    result_content += f"\n\n[VERIFICATION WARNING: {verification['warnings'][0]}]"
                
                if verification['unverified_claims']:
                    print(f"[WARNING] Unverified claims detected: {verification['unverified_claims']}")
            
            response = {
                "messages": [HumanMessage(content=result_content, name="retriever")],
                "next": state["caller"],
                "thought_step": state["thought_step"],
                "caller": "retriever"
            }
            
            return response
            
        except Exception as e:
            print(f"[ERROR] RetrieverAgent process failed: {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_response(state, f"Retriever error: {str(e)}")
    
    def _create_error_response(self, state: AgentState, error_message: str) -> AgentState:
        """Create error response when retrieval fails"""
        return {
            "messages": [HumanMessage(content=f"Retrieval failed: {error_message}. Proceeding with available information.", name="retriever")],
            "next": state["caller"],
            "thought_step": state["thought_step"],
            "caller": "retriever"
        }
    
                    
        