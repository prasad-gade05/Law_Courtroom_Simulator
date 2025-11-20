"""
Enhanced RAG System with Intelligent Chunking, Citation Enforcement, and Hallucination Detection
Implements all 6 priority improvements for the legal courtroom simulator
"""
from typing import List, Dict, Any, Optional, Tuple
from langchain_core.documents import Document
import re
from collections import defaultdict
import numpy as np


class IntelligentChunker:
    """Intelligent chunking that respects legal document structure"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Legal section markers
        self.section_patterns = [
            r'(?:Section|Article|Rule|Chapter)\s+\d+[A-Z]?',
            r'(?:IPC|CrPC|CPC)\s+Section\s+\d+',
            r'\b\d+\.\s+[A-Z]',  # Numbered lists
            r'Case:\s+.+\s+vs\.?\s+.+',  # Case names
        ]
    
    def chunk_document(self, text: str, metadata: Dict = None) -> List[Document]:
        """
        Intelligently chunk document respecting legal structure
        
        Args:
            text: Document text
            metadata: Document metadata
            
        Returns:
            List of chunked documents with preserved legal structure
        """
        metadata = metadata or {}
        
        # First, try to identify major legal sections
        sections = self._identify_legal_sections(text)
        
        if sections:
            # Chunk by legal sections
            chunks = self._chunk_by_sections(sections, metadata)
        else:
            # Fall back to semantic chunking
            chunks = self._semantic_chunk(text, metadata)
        
        return chunks
    
    def _identify_legal_sections(self, text: str) -> List[Tuple[str, str]]:
        """Identify legal sections in text"""
        sections = []
        
        # Find all section headers
        for pattern in self.section_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                sections.append((match.start(), match.group(0)))
        
        # Sort by position
        sections.sort(key=lambda x: x[0])
        
        # Extract text for each section
        section_texts = []
        for i, (pos, header) in enumerate(sections):
            # Find end of this section (start of next section or end of text)
            end_pos = sections[i+1][0] if i+1 < len(sections) else len(text)
            section_text = text[pos:end_pos].strip()
            section_texts.append((header, section_text))
        
        return section_texts
    
    def _chunk_by_sections(self, sections: List[Tuple[str, str]], metadata: Dict) -> List[Document]:
        """Chunk keeping legal sections intact"""
        chunks = []
        
        for header, section_text in sections:
            # If section is small enough, keep it as one chunk
            if len(section_text) <= self.chunk_size:
                chunks.append(Document(
                    page_content=section_text,
                    metadata={**metadata, 'section_header': header}
                ))
            else:
                # Split large sections preserving structure
                sub_chunks = self._split_large_section(section_text, header, metadata)
                chunks.extend(sub_chunks)
        
        return chunks
    
    def _split_large_section(self, text: str, header: str, metadata: Dict) -> List[Document]:
        """Split large sections while preserving meaning"""
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(Document(
                        page_content=current_chunk.strip(),
                        metadata={**metadata, 'section_header': header}
                    ))
                current_chunk = para + "\n\n"
        
        # Add last chunk
        if current_chunk:
            chunks.append(Document(
                page_content=current_chunk.strip(),
                metadata={**metadata, 'section_header': header}
            ))
        
        return chunks
    
    def _semantic_chunk(self, text: str, metadata: Dict) -> List[Document]:
        """Fallback semantic chunking with overlap"""
        chunks = []
        
        # Split by paragraphs
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(Document(
                        page_content=current_chunk.strip(),
                        metadata=metadata
                    ))
                    
                    # Add overlap from previous chunk
                    overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                    current_chunk = overlap_text + para + "\n\n"
                else:
                    current_chunk = para + "\n\n"
        
        # Add last chunk
        if current_chunk:
            chunks.append(Document(
                page_content=current_chunk.strip(),
                metadata=metadata
            ))
        
        return chunks


class LegalReRanker:
    """Re-ranks documents based on legal specificity and relevance"""
    
    def __init__(self):
        # Legal importance signals
        self.importance_signals = {
            'ipc_section': 2.0,  # IPC sections are highly important
            'case_law': 1.8,     # Case precedents are important
            'supreme_court': 2.5,  # Supreme Court cases get highest weight
            'high_court': 2.0,
            'definition': 1.5,
            'punishment': 1.7,
            'evidence': 1.6,
        }
    
    def re_rank(self, query: str, documents: List[Document], top_k: int = 10) -> List[Document]:
        """
        Re-rank documents based on legal specificity
        
        Args:
            query: Search query
            documents: Retrieved documents
            top_k: Number of top documents to return
            
        Returns:
            Re-ranked documents
        """
        if not documents:
            return []
        
        # Score each document
        scored_docs = []
        for doc in documents:
            score = self._calculate_legal_score(query, doc)
            scored_docs.append((score, doc))
        
        # Sort by score (descending)
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        
        return [doc for score, doc in scored_docs[:top_k]]
    
    def _calculate_legal_score(self, query: str, doc: Document) -> float:
        """Calculate legal-specific relevance score"""
        score = 0.0
        content = doc.page_content.lower()
        query_lower = query.lower()
        
        # Base relevance score (keyword matching)
        query_terms = set(query_lower.split())
        content_terms = set(content.split())
        overlap = len(query_terms & content_terms)
        score += overlap * 0.1
        
        # Boost for legal importance signals
        for signal, weight in self.importance_signals.items():
            if signal.replace('_', ' ') in content:
                score += weight
        
        # Boost for specific IPC/legal code mentions
        ipc_mentions = len(re.findall(r'ipc\s+section\s+\d+', content))
        score += ipc_mentions * 1.5
        
        # Boost for case citations
        case_citations = len(re.findall(r'\w+\s+vs\.?\s+\w+', content))
        score += case_citations * 1.0
        
        # Boost if query terms appear in document
        for term in query_terms:
            if len(term) > 3 and term in content:
                score += 0.5
        
        # Boost for metadata quality
        if doc.metadata:
            if 'section_header' in doc.metadata:
                score += 1.0
            if doc.metadata.get('source', '').endswith('.pdf'):
                score += 0.5
        
        return score


class CitationEnforcer:
    """Enforces citation requirements in agent responses"""
    
    def __init__(self):
        self.citation_patterns = [
            r'(?:according to|as per|under)\s+(?:section|ipc\s+section|article)\s+\d+[a-z]?',
            r'in\s+(?:the\s+)?case\s+of\s+\w+\s+vs?\.?\s+\w+',
            r'(?:document|source)\s+#?\d+',
            r'\[.*?\]',  # Citations in brackets
        ]
        
        self.legal_entity_patterns = [
            r'(?:ipc|crpc|cpc)\s+section\s+\d+[a-z]?',
            r'section\s+\d+[a-z]?(?:\s+of\s+(?:the\s+)?(?:ipc|crpc|cpc))?',
            r'article\s+\d+',
        ]
    
    def check_citations(self, text: str) -> Dict[str, Any]:
        """
        Check if text contains proper citations
        
        Returns:
            Dict with citation analysis
        """
        citations_found = []
        
        # Check for citations
        for pattern in self.citation_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                citations_found.append(match.group(0))
        
        # Check for legal entities
        legal_entities = []
        for pattern in self.legal_entity_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                legal_entities.append(match.group(0))
        
        has_citations = len(citations_found) > 0 or len(legal_entities) > 0
        
        return {
            'has_citations': has_citations,
            'citation_count': len(citations_found),
            'legal_entity_count': len(legal_entities),
            'citations': citations_found,
            'legal_entities': legal_entities,
            'citation_density': (len(citations_found) + len(legal_entities)) / max(len(text.split()), 1)
        }
    
    def format_citation_feedback(self, analysis: Dict[str, Any]) -> str:
        """Generate feedback message about citations"""
        if analysis['has_citations']:
            return f"✓ Citations found: {analysis['citation_count']} citations, {analysis['legal_entity_count']} legal references"
        else:
            return "⚠ No citations found. Please cite specific legal sections, cases, or documents."


class EnhancedHallucinationDetector:
    """Enhanced hallucination detection with legal verification"""
    
    def __init__(self):
        self.legal_claim_patterns = [
            r'(?:section|article)\s+\d+[a-z]?\s+(?:states|says|provides|mandates)',
            r'(?:ipc|crpc|cpc)\s+section\s+\d+[a-z]?',
            r'in\s+(?:the\s+)?case\s+of\s+[\w\s]+\s+vs?\.?\s+[\w\s]+,?\s+(?:the\s+)?(?:court|judge|supreme\s+court)\s+(?:held|ruled|stated)',
            r'(?:according to|as per|under)\s+(?:section|ipc)',
        ]
    
    def verify_claims(self, text: str, context_docs: List[Document]) -> Dict[str, Any]:
        """
        Verify legal claims against retrieved context
        
        Args:
            text: Generated text to verify
            context_docs: Retrieved context documents
            
        Returns:
            Verification results
        """
        # Extract legal claims
        claims = self._extract_legal_claims(text)
        
        # Build searchable context
        context_text = "\n".join([doc.page_content for doc in context_docs])
        
        verified_claims = []
        unverified_claims = []
        
        for claim in claims:
            if self._verify_claim_in_context(claim, context_text, context_docs):
                verified_claims.append(claim)
            else:
                unverified_claims.append(claim)
        
        # Calculate confidence
        total_claims = len(claims)
        confidence = len(verified_claims) / total_claims if total_claims > 0 else 1.0
        
        return {
            'is_grounded': len(unverified_claims) == 0,
            'confidence': confidence,
            'total_claims': total_claims,
            'verified_claims': verified_claims,
            'unverified_claims': unverified_claims,
            'verification_rate': f"{len(verified_claims)}/{total_claims}",
            'warnings': self._generate_warnings(confidence, unverified_claims)
        }
    
    def _extract_legal_claims(self, text: str) -> List[str]:
        """Extract legal claims from text"""
        claims = []
        
        for pattern in self.legal_claim_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get surrounding context (full sentence)
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                claim = text[start:end].strip()
                claims.append(claim)
        
        return claims
    
    def _verify_claim_in_context(self, claim: str, context_text: str, context_docs: List[Document]) -> bool:
        """Verify if a claim is supported by context"""
        claim_lower = claim.lower()
        context_lower = context_text.lower()
        
        # Extract key legal identifiers (section numbers, case names, etc.)
        identifiers = self._extract_identifiers(claim)
        
        if not identifiers:
            # No specific identifiers, do fuzzy match
            claim_words = set(claim_lower.split())
            context_words = set(context_lower.split())
            overlap = len(claim_words & context_words)
            return overlap / len(claim_words) > 0.6 if claim_words else False
        
        # Check if all identifiers exist in context
        for identifier in identifiers:
            if identifier.lower() not in context_lower:
                return False
        
        return True
    
    def _extract_identifiers(self, text: str) -> List[str]:
        """Extract legal identifiers (section numbers, case names)"""
        identifiers = []
        
        # Section numbers
        section_matches = re.findall(r'(?:section|ipc|crpc|cpc)\s+\d+[a-z]?', text, re.IGNORECASE)
        identifiers.extend(section_matches)
        
        # Case names
        case_matches = re.findall(r'\w+\s+vs?\.?\s+\w+', text, re.IGNORECASE)
        identifiers.extend(case_matches)
        
        return identifiers
    
    def _generate_warnings(self, confidence: float, unverified_claims: List[str]) -> List[str]:
        """Generate warnings based on verification results"""
        warnings = []
        
        if confidence < 0.5:
            warnings.append("⚠ LOW CONFIDENCE: Many claims cannot be verified against retrieved documents")
        elif confidence < 0.7:
            warnings.append("⚠ MEDIUM CONFIDENCE: Some claims may not be fully supported")
        
        if unverified_claims:
            warnings.append(f"⚠ {len(unverified_claims)} unverified claim(s) found")
        
        return warnings


class StructuredContextFormatter:
    """Formats retrieved context in structured, easy-to-reference format"""
    
    def format_context(self, documents: List[Document], case_description: str = "") -> str:
        """
        Format documents into structured context with sections
        
        Args:
            documents: Retrieved documents
            case_description: Original case description
            
        Returns:
            Structured context string
        """
        if not documents:
            return "No legal documents retrieved."
        
        # Categorize documents
        categories = self._categorize_documents(documents)
        
        # Build structured context
        context_parts = []
        
        context_parts.append("=" * 80)
        context_parts.append("COMPREHENSIVE LEGAL CONTEXT")
        context_parts.append("=" * 80)
        context_parts.append("")
        
        # Add case description summary
        if case_description:
            context_parts.append("📋 CASE OVERVIEW:")
            context_parts.append(case_description[:500] + "..." if len(case_description) > 500 else case_description)
            context_parts.append("")
        
        # Add categorized sections
        for category, docs in categories.items():
            if docs:
                context_parts.append(f"\n{'=' * 80}")
                context_parts.append(f"📚 {category.upper()}")
                context_parts.append(f"{'=' * 80}")
                context_parts.append("")
                
                for i, doc in enumerate(docs, 1):
                    source = doc.metadata.get('filename', doc.metadata.get('source', 'Unknown'))
                    section_header = doc.metadata.get('section_header', '')
                    
                    context_parts.append(f"[{category[:3].upper()}-{i}] Source: {source}")
                    if section_header:
                        context_parts.append(f"Section: {section_header}")
                    context_parts.append("-" * 80)
                    context_parts.append(doc.page_content)
                    context_parts.append("")
        
        context_parts.append("=" * 80)
        context_parts.append("END OF LEGAL CONTEXT")
        context_parts.append("=" * 80)
        context_parts.append("")
        context_parts.append("CITATION INSTRUCTIONS:")
        context_parts.append("When referencing this context, cite as: [CATEGORY-NUMBER], e.g., [IPC-1], [CAS-2]")
        context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _categorize_documents(self, documents: List[Document]) -> Dict[str, List[Document]]:
        """Categorize documents by type"""
        categories = {
            'IPC Sections': [],
            'Case Precedents': [],
            'Legal Principles': [],
            'Evidence & Facts': [],
            'Procedural Law': [],
            'Other': []
        }
        
        for doc in documents:
            content_lower = doc.page_content.lower()
            
            if 'ipc section' in content_lower or 'indian penal code' in content_lower:
                categories['IPC Sections'].append(doc)
            elif 'case' in content_lower and ('vs' in content_lower or 'versus' in content_lower):
                categories['Case Precedents'].append(doc)
            elif any(word in content_lower for word in ['crpc', 'cpc', 'procedure', 'evidence act']):
                categories['Procedural Law'].append(doc)
            elif any(word in content_lower for word in ['principle', 'doctrine', 'rule of law']):
                categories['Legal Principles'].append(doc)
            elif any(word in content_lower for word in ['evidence', 'witness', 'testimony', 'forensic']):
                categories['Evidence & Facts'].append(doc)
            else:
                categories['Other'].append(doc)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}


class IntelligentContextCompressor:
    """Compress context while preserving legal citations and key information"""
    
    def __init__(self, max_chars: int = 15000):
        self.max_chars = max_chars
    
    def compress(self, documents: List[Document], query: str) -> List[Document]:
        """
        Compress documents intelligently, preserving legal citations
        
        Args:
            documents: Documents to compress
            query: Original query for relevance scoring
            
        Returns:
            Compressed documents
        """
        if not documents:
            return []
        
        # Calculate total size
        total_chars = sum(len(doc.page_content) for doc in documents)
        
        if total_chars <= self.max_chars:
            return documents  # No compression needed
        
        # Score documents by importance
        scored_docs = []
        for doc in documents:
            importance = self._calculate_importance(doc, query)
            scored_docs.append((importance, doc))
        
        # Sort by importance
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        
        # Select documents until we hit the limit
        compressed = []
        current_chars = 0
        
        for importance, doc in scored_docs:
            doc_chars = len(doc.page_content)
            
            if current_chars + doc_chars <= self.max_chars:
                compressed.append(doc)
                current_chars += doc_chars
            else:
                # Try to include a summary of this document
                remaining = self.max_chars - current_chars
                if remaining > 200:
                    summary = self._extract_key_points(doc, remaining)
                    if summary:
                        compressed.append(Document(
                            page_content=summary,
                            metadata={**doc.metadata, 'compressed': True}
                        ))
                break
        
        return compressed
    
    def _calculate_importance(self, doc: Document, query: str) -> float:
        """Calculate importance score for document"""
        score = 0.0
        content = doc.page_content.lower()
        
        # Legal citations are important
        ipc_mentions = len(re.findall(r'ipc\s+section\s+\d+', content))
        score += ipc_mentions * 5.0
        
        # Case citations are important
        case_mentions = len(re.findall(r'\w+\s+vs\.?\s+\w+', content))
        score += case_mentions * 3.0
        
        # Query relevance
        query_terms = set(query.lower().split())
        content_terms = set(content.split())
        overlap = len(query_terms & content_terms)
        score += overlap * 2.0
        
        # Metadata quality
        if doc.metadata.get('section_header'):
            score += 5.0
        
        return score
    
    def _extract_key_points(self, doc: Document, max_chars: int) -> str:
        """Extract key points from document"""
        content = doc.page_content
        
        # Look for legal citations and keep them
        citations = re.findall(r'(?:IPC|CrPC|CPC)?\s*[Ss]ection\s+\d+[A-Za-z]?[^.]*\.', content)
        
        if citations:
            summary = "KEY POINTS: " + " ".join(citations[:3])
            return summary[:max_chars]
        
        # Otherwise return first part
        return content[:max_chars] + "..."


class EnhancedRAGSystem:
    """Main enhanced RAG system coordinating all improvements"""
    
    def __init__(self, vector_retriever, documents: List[Document] = None, vector_store = None):
        self.vector_retriever = vector_retriever
        self.documents = documents or []
        self.vector_store = vector_store
        
        # Initialize all components
        self.chunker = IntelligentChunker()
        self.re_ranker = LegalReRanker()
        self.citation_enforcer = CitationEnforcer()
        self.hallucination_detector = EnhancedHallucinationDetector()
        self.context_formatter = StructuredContextFormatter()
        self.compressor = IntelligentContextCompressor()
    
    def retrieve_and_structure(
        self, 
        query: str, 
        k: int = 15,
        case_description: str = ""
    ) -> Tuple[str, List[Document], Dict[str, Any]]:
        """
        Complete RAG pipeline with all enhancements
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            case_description: Original case description
            
        Returns:
            Tuple of (formatted_context, documents, metadata)
        """
        # 1. Retrieve documents
        retrieved_docs = self.vector_retriever.invoke(query)[:k]
        
        # 2. Re-rank by legal specificity
        re_ranked_docs = self.re_ranker.re_rank(query, retrieved_docs, top_k=k)
        
        # 3. Compress intelligently
        compressed_docs = self.compressor.compress(re_ranked_docs, query)
        
        # 4. Format as structured context
        formatted_context = self.context_formatter.format_context(
            compressed_docs, 
            case_description
        )
        
        metadata = {
            'retrieved_count': len(retrieved_docs),
            're_ranked_count': len(re_ranked_docs),
            'compressed_count': len(compressed_docs),
            'context_size': len(formatted_context),
            'query': query
        }
        
        return formatted_context, compressed_docs, metadata
    
    def verify_response(
        self, 
        response_text: str, 
        context_docs: List[Document]
    ) -> Dict[str, Any]:
        """
        Verify agent response for citations and hallucinations
        
        Args:
            response_text: Generated response
            context_docs: Context used for generation
            
        Returns:
            Verification results
        """
        # Check citations
        citation_analysis = self.citation_enforcer.check_citations(response_text)
        
        # Check for hallucinations
        hallucination_analysis = self.hallucination_detector.verify_claims(
            response_text, 
            context_docs
        )
        
        return {
            'citations': citation_analysis,
            'hallucinations': hallucination_analysis,
            'overall_quality': self._calculate_quality_score(
                citation_analysis, 
                hallucination_analysis
            )
        }
    
    def _calculate_quality_score(
        self, 
        citation_analysis: Dict, 
        hallucination_analysis: Dict
    ) -> Dict[str, Any]:
        """Calculate overall response quality score"""
        # Citation score (0-50)
        citation_score = min(50, citation_analysis['citation_density'] * 1000)
        
        # Hallucination score (0-50)
        hallucination_score = hallucination_analysis['confidence'] * 50
        
        total_score = citation_score + hallucination_score
        
        return {
            'total_score': total_score,
            'max_score': 100,
            'percentage': f"{total_score:.1f}%",
            'grade': self._score_to_grade(total_score),
            'citation_score': citation_score,
            'hallucination_score': hallucination_score
        }
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A+ (Excellent)"
        elif score >= 80:
            return "A (Very Good)"
        elif score >= 70:
            return "B (Good)"
        elif score >= 60:
            return "C (Acceptable)"
        else:
            return "D (Needs Improvement)"
