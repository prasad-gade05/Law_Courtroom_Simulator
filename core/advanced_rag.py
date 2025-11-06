"""
Advanced RAG module with re-ranking, context compression, and hallucination detection
"""
from typing import List, Dict, Any, Optional, Tuple
from langchain_core.documents import Document
import re
from collections import defaultdict
import numpy as np


class HallucinationDetector:
    """Detects potential hallucinations in generated text"""
    
    def __init__(self):
        self.hallucination_patterns = [
            r"according to (section|article|case) \d+",  # Legal citations
            r"(IPC|CrPC|CPC) section \d+",  # Indian legal codes
            r"in the case of .+ vs .+",  # Case references
            r"the (supreme court|high court) ruled",  # Court rulings
        ]
    
    def verify_against_context(self, generated_text: str, context_docs: List[Document]) -> Dict[str, Any]:
        """
        Verify if generated text is grounded in the provided context
        
        Returns:
            Dict with verification results and confidence score
        """
        # Extract all citations and claims from generated text
        citations = self._extract_citations(generated_text)
        
        # Build context text from documents
        context_text = "\n".join([doc.page_content for doc in context_docs])
        
        verification_results = {
            "is_grounded": True,
            "confidence": 1.0,
            "unverified_claims": [],
            "verified_claims": [],
            "warnings": []
        }
        
        # Check each citation against context
        for citation in citations:
            if self._is_citation_in_context(citation, context_text):
                verification_results["verified_claims"].append(citation)
            else:
                verification_results["unverified_claims"].append(citation)
                verification_results["is_grounded"] = False
        
        # Calculate confidence score
        if citations:
            verified_ratio = len(verification_results["verified_claims"]) / len(citations)
            verification_results["confidence"] = verified_ratio
        
        # Add warnings for low confidence
        if verification_results["confidence"] < 0.7:
            verification_results["warnings"].append(
                f"Low verification confidence ({verification_results['confidence']:.2%}). "
                f"Some claims may not be supported by available documents."
            )
        
        return verification_results
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract legal citations and specific claims from text"""
        citations = []
        
        for pattern in self.hallucination_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                citations.append(match.group(0))
        
        return citations
    
    def _is_citation_in_context(self, citation: str, context: str) -> bool:
        """Check if citation exists in context (fuzzy matching)"""
        # Normalize both strings
        citation_norm = citation.lower().strip()
        context_norm = context.lower()
        
        # Direct substring match
        if citation_norm in context_norm:
            return True
        
        # Extract key numbers/identifiers and check if they exist
        numbers = re.findall(r'\d+', citation)
        if numbers:
            # Check if any of the numbers appear in context with similar keywords
            for num in numbers:
                if num in context_norm:
                    # Found the number, now check if surrounding context is similar
                    citation_keywords = set(re.findall(r'\w+', citation_norm))
                    # Find context around the number
                    num_pos = context_norm.find(num)
                    if num_pos >= 0:
                        context_window = context_norm[max(0, num_pos-100):num_pos+100]
                        context_keywords = set(re.findall(r'\w+', context_window))
                        # Check overlap
                        overlap = len(citation_keywords & context_keywords)
                        if overlap >= len(citation_keywords) * 0.5:
                            return True
        
        return False


class ContextCompressor:
    """Compress and filter retrieved documents to most relevant content"""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
    
    def compress(self, query: str, documents: List[Document], top_k: int = 5) -> List[Document]:
        """
        Compress documents by selecting most relevant passages
        
        Args:
            query: The search query
            documents: Retrieved documents
            top_k: Number of documents to return
            
        Returns:
            Compressed list of most relevant documents
        """
        if not documents:
            return []
        
        # Score documents by relevance
        scored_docs = []
        for doc in documents:
            score = self._relevance_score(query, doc.page_content)
            scored_docs.append((score, doc))
        
        # Sort by score (descending)
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        
        # Take top_k documents
        top_docs = [doc for score, doc in scored_docs[:top_k]]
        
        # Further compress if needed to fit token budget
        compressed_docs = self._fit_token_budget(top_docs)
        
        return compressed_docs
    
    def _relevance_score(self, query: str, text: str) -> float:
        """Calculate relevance score between query and text"""
        query_terms = set(query.lower().split())
        text_terms = set(text.lower().split())
        
        # Jaccard similarity
        intersection = query_terms & text_terms
        union = query_terms | text_terms
        
        if not union:
            return 0.0
        
        jaccard = len(intersection) / len(union)
        
        # Bonus for exact phrase matches
        exact_match_bonus = 0.0
        if query.lower() in text.lower():
            exact_match_bonus = 0.3
        
        return jaccard + exact_match_bonus
    
    def _fit_token_budget(self, documents: List[Document]) -> List[Document]:
        """Ensure documents fit within token budget"""
        # Rough estimate: 1 token ≈ 4 characters
        char_budget = self.max_tokens * 4
        
        current_chars = 0
        fitted_docs = []
        
        for doc in documents:
            doc_chars = len(doc.page_content)
            if current_chars + doc_chars <= char_budget:
                fitted_docs.append(doc)
                current_chars += doc_chars
            else:
                # Try to include a truncated version
                remaining = char_budget - current_chars
                if remaining > 500:  # Only if we can include meaningful content
                    truncated_doc = Document(
                        page_content=doc.page_content[:remaining] + "...",
                        metadata=doc.metadata
                    )
                    fitted_docs.append(truncated_doc)
                break
        
        return fitted_docs


class HybridRetriever:
    """Combines vector search with BM25 for better retrieval"""
    
    def __init__(self, vector_retriever, documents: List[Document] = None):
        self.vector_retriever = vector_retriever
        self.documents = documents or []
        self.bm25 = None
        self._initialize_bm25()
    
    def _initialize_bm25(self):
        """Initialize BM25 index if documents are available"""
        if not self.documents:
            return
        
        try:
            from rank_bm25 import BM25Okapi
            
            # Tokenize documents for BM25
            tokenized_docs = [doc.page_content.lower().split() for doc in self.documents]
            self.bm25 = BM25Okapi(tokenized_docs)
        except ImportError:
            print("[WARNING] rank_bm25 not installed, using vector search only")
            self.bm25 = None
    
    def retrieve(self, query: str, k: int = 10) -> List[Document]:
        """
        Hybrid retrieval combining vector search and BM25
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
        Returns:
            List of most relevant documents
        """
        # Get results from vector search
        vector_results = self.vector_retriever.invoke(query)
        
        # If BM25 is not available, return vector results only
        if not self.bm25 or not self.documents:
            return vector_results[:k]
        
        # Get results from BM25
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Get top k indices from BM25
        top_bm25_indices = np.argsort(bm25_scores)[::-1][:k]
        bm25_results = [self.documents[i] for i in top_bm25_indices if bm25_scores[i] > 0]
        
        # Combine results with reciprocal rank fusion
        combined_results = self._reciprocal_rank_fusion(
            [vector_results[:k], bm25_results],
            k=k
        )
        
        return combined_results
    
    def _reciprocal_rank_fusion(self, result_lists: List[List[Document]], k: int = 10) -> List[Document]:
        """
        Combine multiple ranked lists using Reciprocal Rank Fusion
        
        Args:
            result_lists: List of ranked document lists
            k: Number of final results to return
            
        Returns:
            Fused and re-ranked list of documents
        """
        # Score documents using RRF
        doc_scores = defaultdict(float)
        
        for result_list in result_lists:
            for rank, doc in enumerate(result_list, 1):
                # Use page_content as unique identifier
                doc_id = doc.page_content[:100]  # First 100 chars as ID
                doc_scores[doc_id] += 1.0 / (rank + 60)  # RRF formula
        
        # Sort by score
        sorted_doc_ids = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Retrieve original documents
        doc_map = {}
        for result_list in result_lists:
            for doc in result_list:
                doc_id = doc.page_content[:100]
                if doc_id not in doc_map:
                    doc_map[doc_id] = doc
        
        # Return top k documents
        return [doc_map[doc_id] for doc_id, score in sorted_doc_ids[:k] if doc_id in doc_map]


class RetrievalAugmentor:
    """Main class coordinating all advanced RAG techniques"""
    
    def __init__(self, vector_retriever, documents: List[Document] = None):
        self.hybrid_retriever = HybridRetriever(vector_retriever, documents)
        self.compressor = ContextCompressor(max_tokens=4000)
        self.hallucination_detector = HallucinationDetector()
    
    def retrieve_and_compress(self, query: str, k: int = 10, top_k_compressed: int = 5) -> Tuple[List[Document], Dict[str, Any]]:
        """
        Retrieve, re-rank, and compress documents
        
        Args:
            query: Search query
            k: Initial number of documents to retrieve
            top_k_compressed: Number of documents after compression
            
        Returns:
            Tuple of (compressed documents, metadata)
        """
        # Hybrid retrieval
        retrieved_docs = self.hybrid_retriever.retrieve(query, k=k)
        
        # Compress to most relevant content
        compressed_docs = self.compressor.compress(query, retrieved_docs, top_k=top_k_compressed)
        
        metadata = {
            "retrieved_count": len(retrieved_docs),
            "compressed_count": len(compressed_docs),
            "query": query
        }
        
        return compressed_docs, metadata
    
    def verify_response(self, response_text: str, context_docs: List[Document]) -> Dict[str, Any]:
        """
        Verify if response is grounded in context
        
        Args:
            response_text: Generated response text
            context_docs: Context documents used for generation
            
        Returns:
            Verification results
        """
        return self.hallucination_detector.verify_against_context(response_text, context_docs)
    
    def format_context_for_prompt(self, documents: List[Document], include_metadata: bool = True) -> str:
        """
        Format retrieved documents for inclusion in prompt
        
        Args:
            documents: Retrieved documents
            include_metadata: Whether to include document metadata
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant documents found in the database."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"--- Document {i} ---")
            if include_metadata and doc.metadata:
                source = doc.metadata.get('filename', doc.metadata.get('source', 'Unknown'))
                context_parts.append(f"Source: {source}")
            context_parts.append(doc.page_content)
            context_parts.append("")  # Empty line between documents
        
        return "\n".join(context_parts)
