from typing import Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from core.chroma_store import ChromaVectorStore
from core.advanced_rag import RetrievalAugmentor
from core.enhanced_rag_system import EnhancedRAGSystem
from .base import AgentState, safe_get_content
import os
from dotenv import load_dotenv
load_dotenv()


class InitialRetrieverAgent:
    """Agent that performs comprehensive document retrieval at the start of the trial"""
    
    def __init__(self, llms):
        self.llms = llms
        
        # Initialize retrievers
        self.private_retriever = self._create_retriever(private=True)
        self.public_retriever = self._create_retriever(private=False)
        
        self.system_prompt = """
You are a legal research assistant that performs COMPREHENSIVE document retrieval at the START of a trial.

Your task:
1. Analyze the case description provided
2. Identify ALL relevant legal topics, IPC sections, precedents, and case law that might be needed
3. Formulate broad queries to retrieve comprehensive legal context
4. Return a complete set of legal information that both prosecution and defense can use

Be thorough - fetch documents covering:
- Relevant IPC sections mentioned or implied
- Related case precedents
- Legal principles and defenses
- Burden of proof and procedural aspects

Output Format:
List 3-5 comprehensive search queries that cover all aspects of the case, one per line.
Example:
IPC Section 302 murder and punishment
IPC Section 304 culpable homicide not amounting to murder
Self-defense provisions IPC Section 96-106
Burden of proof in criminal cases India
"""

    def _create_retriever(self, private=False):
        """Create ChromaDB vector store with enhanced RAG capabilities"""
        if private:
            vector_store = ChromaVectorStore('private', './private_documents')
        else:
            vector_store = ChromaVectorStore('public', './public_documents')

        base_retriever = vector_store.as_retriever()
        
        try:
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
            print(f"[WARNING] Could not get documents: {e}")
            documents = []
        
        # Use enhanced RAG system with all improvements
        enhanced_rag = EnhancedRAGSystem(base_retriever, documents, vector_store=vector_store)
        return enhanced_rag

    async def process(self, state: AgentState) -> AgentState:
        """Perform comprehensive initial document retrieval"""
        
        print("\n" + "="*60)
        print("[INITIAL RETRIEVAL] Starting comprehensive document fetch")
        print("="*60)
        
        try:
            # Get case description from first message
            case_description = state["messages"][0].content if state["messages"] else ""
            
            # Generate comprehensive queries
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Case Description:\n{case_description}\n\nGenerate comprehensive search queries:"}
            ]
            
            queries_response = None
            for i, llm in enumerate(self.llms):
                try:
                    queries_response = llm.invoke(messages)
                    break
                except Exception as e:
                    print(f"LLM {i} failed: {e}")
                    continue
            
            if not queries_response:
                return self._create_fallback_response(state, case_description)
            
            # Extract queries
            queries_text = safe_get_content(queries_response)
            queries = [q.strip() for q in queries_text.split('\n') if q.strip() and len(q.strip()) > 10]
            
            print(f"\n[INITIAL RETRIEVAL] Generated {len(queries)} queries:")
            for i, q in enumerate(queries, 1):
                safe_q = q.encode('ascii', errors='replace').decode('ascii')
                print(f"  {i}. {safe_q}")
            
            # Retrieve documents for all queries using enhanced RAG
            all_retrieved_docs = []
            all_formatted_contexts = []
            
            for query in queries[:5]:  # Limit to 5 queries max
                safe_query = query[:80].encode('ascii', errors='replace').decode('ascii')
                print(f"\n[RETRIEVAL] Query: {safe_query}...")
                
                # Try public retriever (IPC, case law, etc.) with enhanced RAG
                try:
                    formatted_context, docs, meta = self.public_retriever.retrieve_and_structure(
                        query, k=10, case_description=case_description[:500]
                    )
                    all_retrieved_docs.extend(docs)
                    all_formatted_contexts.append(formatted_context)
                    print(f"  Public: Retrieved {meta['retrieved_count']}, compressed to {meta['compressed_count']}")
                    print(f"  Context size: {meta['context_size']} chars")
                except Exception as e:
                    print(f"  Public retrieval error: {e}")
                
                # Try private retriever (user's case files)
                try:
                    formatted_context, docs, meta = self.private_retriever.retrieve_and_structure(
                        query, k=5, case_description=case_description[:500]
                    )
                    all_retrieved_docs.extend(docs)
                    all_formatted_contexts.append(formatted_context)
                    print(f"  Private: Retrieved {meta['retrieved_count']}, compressed to {meta['compressed_count']}")
                except Exception as e:
                    print(f"  Private retrieval error: {e}")
            
            # Combine all formatted contexts
            retrieved_context = "\n\n".join(all_formatted_contexts)
            
            print(f"\n[INITIAL RETRIEVAL] Total documents retrieved: {len(all_retrieved_docs)}")
            print(f"[INITIAL RETRIEVAL] Context size: {len(retrieved_context)} characters")
            print("="*60)
            
            # Create informative message
            summary_msg = f"""[ENHANCED LEGAL CONTEXT RETRIEVED]

✓ Intelligent chunking applied - legal sections preserved
✓ Re-ranked by legal specificity (IPC, case law, precedents)
✓ Structured format with categories (IPC, Cases, Evidence, etc.)
✓ Context compressed intelligently - key citations preserved

Retrieved comprehensive legal information covering:
- {len(queries)} legal topics analyzed
- {len(all_retrieved_docs)} relevant document chunks (re-ranked & compressed)
- Total context: {len(retrieved_context)} characters

This context is structured for easy reference with citation markers [IPC-1], [CAS-2], etc.
All agents MUST cite sources when making legal arguments.
Proceeding to opening statements..."""
            
            return {
                "messages": [HumanMessage(content=summary_msg, name="initial_retriever")],
                "next": "prosecutor",
                "thought_step": 0,
                "caller": "initial_retriever",
                "initial_retrieval_done": True,
                "retrieved_context": retrieved_context,
                "retrieved_docs": all_retrieved_docs,  # Store docs for verification
                "iteration_count": state.get("iteration_count", 0)
            }
            
        except Exception as e:
            print(f"[ERROR] Initial retrieval failed: {e}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_response(state, "")
    
    def _format_comprehensive_context(self, docs: List) -> str:
        """Format retrieved documents into a comprehensive context string"""
        if not docs:
            return "No additional legal context retrieved."
        
        context_parts = []
        context_parts.append("=== RETRIEVED LEGAL CONTEXT ===\n")
        
        for i, doc in enumerate(docs, 1):
            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            source = metadata.get('filename', 'Unknown source')
            
            context_parts.append(f"\n[Document {i}] Source: {source}")
            context_parts.append(content[:500])  # Limit each chunk to 500 chars
            context_parts.append("...")
        
        context_parts.append("\n=== END OF LEGAL CONTEXT ===")
        return "\n".join(context_parts)
    
    def _create_fallback_response(self, state: AgentState, case_description: str) -> AgentState:
        """Create fallback response if retrieval fails"""
        fallback_queries = [
            "Indian Penal Code criminal law provisions",
            "Criminal case precedents India",
            "Burden of proof criminal cases"
        ]
        
        print("[FALLBACK] Using fallback queries...")
        
        all_docs = []
        formatted_contexts = []
        for query in fallback_queries:
            try:
                formatted_context, docs, meta = self.public_retriever.retrieve_and_structure(
                    query, k=5, case_description=case_description[:500]
                )
                all_docs.extend(docs)
                formatted_contexts.append(formatted_context)
            except:
                pass
        
        context = "\n\n".join(formatted_contexts) if formatted_contexts else "Basic legal context retrieved."
        
        return {
            "messages": [HumanMessage(content="[LEGAL CONTEXT] Basic legal context retrieved. Proceeding to trial...", name="initial_retriever")],
            "next": "prosecutor",
            "thought_step": 0,
            "caller": "initial_retriever",
            "initial_retrieval_done": True,
            "retrieved_context": context,
            "retrieved_docs": all_docs,
            "iteration_count": state.get("iteration_count", 0)
        }
