"""
Document Summarization Agent - Summarizes large legal documents before adding to vector store
"""
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage
from .base import AgentState, safe_get_content
import os
from pathlib import Path


class DocumentSummarizationAgent:
    """
    Agent that summarizes large legal documents into concise, relevant summaries
    before they are added to the vector database. This prevents database flooding
    and improves retrieval quality.
    """
    
    def __init__(self, llms):
        self.llms = llms
        self.system_prompt = """You are a legal document summarization expert. Your role is to create concise, high-quality summaries of legal documents that preserve all critical information.

CRITICAL REQUIREMENTS:
1. Extract and preserve ALL key legal information:
   - Case names, parties involved
   - Court names and jurisdictions
   - Section numbers and legal provisions cited
   - Key legal principles and holdings
   - Relevant facts and circumstances
   - Final judgment/decision

2. Summarization Guidelines:
   - Target length: 500-800 words (adjust based on document complexity)
   - Preserve exact legal citations (IPC sections, case names)
   - Keep important dates and numbers
   - Maintain legal terminology accuracy
   - Structure: Summary → Key Points → Legal Provisions → Conclusion

3. Format:
   **Document Summary:**
   [Concise 2-3 sentence overview]
   
   **Key Legal Points:**
   - [Point 1]
   - [Point 2]
   - [Point 3]
   
   **Legal Provisions Cited:**
   - [IPC Section X: Description]
   - [Case Name: Principle]
   
   **Judgment/Conclusion:**
   [Final decision or key takeaway]

4. Quality Standards:
   - NO information loss on legal citations
   - NO fabrication of information
   - Preserve case law precedents exactly
   - Keep section numbers accurate
   - Maintain context for proper understanding

Your summaries will be indexed in a vector database for legal research, so accuracy is critical.
"""
    
    async def summarize_document(self, document_path: str, document_content: str) -> Dict[str, Any]:
        """
        Summarize a single legal document with chunked processing for large documents
        
        Args:
            document_path: Path to the document file
            document_content: Full content of the document
            
        Returns:
            Dict with summary and metadata
        """
        # Check if document is already small enough
        if len(document_content) < 2000:  # Already small, no need to summarize
            print(f"  Document is small ({len(document_content)} chars), using as-is")
            return {
                "summary": document_content,
                "original_length": len(document_content),
                "summary_length": len(document_content),
                "compression_ratio": 1.0,
                "source": document_path,
                "needs_summary": False
            }
        
        print(f"  Document length: {len(document_content)} chars - summarizing...")
        
        # For very large documents (>50K chars), use chunked summarization
        if len(document_content) > 50000:
            print(f"  Large document detected - using chunked summarization")
            summary = await self._summarize_large_document(document_path, document_content)
        else:
            # Regular summarization for smaller documents
            summary = await self._summarize_single_chunk(document_path, document_content)
        
        if not summary:
            # Fallback: extract key sections intelligently
            print(f"  Using intelligent fallback extraction")
            summary = self._extract_key_sections(document_content)
        
        compression_ratio = len(summary) / len(document_content)
        
        return {
            "summary": summary,
            "original_length": len(document_content),
            "summary_length": len(summary),
            "compression_ratio": compression_ratio,
            "source": document_path,
            "needs_summary": True
        }
    
    async def _summarize_single_chunk(self, document_path: str, document_content: str) -> str:
        """Summarize a document that fits in one LLM call"""
        prompt = f"""Summarize the following legal document according to the guidelines provided.

Document Source: {document_path}
Document Length: {len(document_content)} characters

=== DOCUMENT CONTENT ===
{document_content[:30000]}  # Limit to 30K chars for safety
=== END DOCUMENT ===

Provide a comprehensive yet concise summary following the specified format.
"""
        
        # Get summary from LLM
        for i, llm in enumerate(self.llms):
            try:
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ]
                result = llm.invoke(messages)
                summary = safe_get_content(result)
                print(f"  Summary generated by LLM {i} ({len(summary)} chars)")
                return summary
            except Exception as e:
                print(f"  LLM {i} failed: {e}")
                continue
        
        return None
    
    async def _summarize_large_document(self, document_path: str, document_content: str) -> str:
        """
        Summarize very large documents by breaking into chunks and summarizing each
        """
        # Split document into manageable chunks (20K chars each with overlap)
        chunk_size = 20000
        overlap = 1000
        chunks = []
        
        for i in range(0, len(document_content), chunk_size - overlap):
            chunk = document_content[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        
        print(f"  Split into {len(chunks)} chunks for processing")
        
        # Summarize each chunk
        chunk_summaries = []
        for idx, chunk in enumerate(chunks[:5], 1):  # Limit to first 5 chunks
            print(f"    Processing chunk {idx}/{min(len(chunks), 5)}...", end='', flush=True)
            
            prompt = f"""Summarize this section of a legal document. Focus on key legal points, citations, and decisions.

Document: {document_path}
Section: {idx}/{len(chunks)}

=== SECTION CONTENT ===
{chunk}
=== END SECTION ===

Provide a concise summary (200-300 words) of the key legal information in this section.
"""
            
            summary = None
            for llm in self.llms:
                try:
                    messages = [
                        {"role": "system", "content": "You are a legal document summarizer. Extract key legal information concisely."},
                        {"role": "user", "content": prompt}
                    ]
                    result = llm.invoke(messages)
                    summary = safe_get_content(result)
                    break
                except Exception as e:
                    continue
            
            if summary:
                chunk_summaries.append(f"**Section {idx}:**\n{summary}")
                print(f" [OK] ({len(summary)} chars)")
            else:
                # Fallback: use first 500 chars of chunk
                chunk_summaries.append(f"**Section {idx}:**\n{chunk[:500]}...")
                print(f" [FALLBACK]")
        
        # Combine all chunk summaries
        combined = "\n\n".join(chunk_summaries)
        
        # If combined is still too long, do a final summarization pass
        if len(combined) > 3000:
            print(f"  Final consolidation pass...")
            final_prompt = f"""Consolidate these section summaries into a single coherent summary.

Document: {document_path}

=== SECTION SUMMARIES ===
{combined}
=== END SUMMARIES ===

Create a unified summary (500-800 words) covering:
1. Case overview and parties involved
2. Key legal issues and provisions cited
3. Main arguments and evidence
4. Judgment/conclusion (if present)
"""
            
            for llm in self.llms:
                try:
                    messages = [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": final_prompt}
                    ]
                    result = llm.invoke(messages)
                    final_summary = safe_get_content(result)
                    print(f"  Final summary: {len(final_summary)} chars")
                    return final_summary
                except Exception as e:
                    continue
        
        # Return combined summaries if final pass fails
        return combined
    
    def _extract_key_sections(self, document_content: str) -> str:
        """
        Intelligent fallback: extract key sections from document
        Looks for headings, case names, judgments, etc.
        """
        lines = document_content.split('\n')
        key_lines = []
        
        # Keywords that indicate important sections
        keywords = [
            'supreme court', 'high court', 'judgment', 'held:', 'held that',
            'section', 'ipc', 'crpc', 'vs.', 'v.', 'appellant', 'respondent',
            'facts', 'issue', 'decision', 'ratio', 'conclusion', 'order'
        ]
        
        for line in lines[:500]:  # First 500 lines
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                key_lines.append(line)
            elif len(line) > 50 and line[0].isupper():  # Potential heading
                key_lines.append(line)
        
        # Take first 3000 chars of extracted lines
        extracted = '\n'.join(key_lines)[:3000]
        
        return f"""**Document Summary (Extracted Key Sections):**

{extracted}

**Note:** This is an automatically extracted summary due to document size. Full document available in source file.

**Extraction Method:** Key legal terms and section headings
**Source:** {len(document_content):,} characters processed
"""
    
    async def process_new_documents(self, directory: str = "public_documents") -> Dict[str, Any]:
        """
        Process all new documents in the directory, summarize them, and prepare for indexing
        
        Args:
            directory: Directory containing documents to process
            
        Returns:
            Dict with processing results and summaries
        """
        print("\n" + "="*80)
        print("DOCUMENT SUMMARIZATION AGENT - STARTED")
        print("="*80)
        print(f"Processing directory: {directory}")
        
        doc_dir = Path(directory)
        if not doc_dir.exists():
            print(f"Directory not found: {directory}")
            return {
                "processed_count": 0,
                "summaries": [],
                "total_original_size": 0,
                "total_summary_size": 0
            }
        
        # Find all text documents
        document_files = list(doc_dir.glob("*.txt"))
        print(f"Found {len(document_files)} documents to process")
        
        if not document_files:
            print("No documents to process")
            return {
                "processed_count": 0,
                "summaries": [],
                "total_original_size": 0,
                "total_summary_size": 0
            }
        
        summaries = []
        total_original_size = 0
        total_summary_size = 0
        
        for idx, doc_file in enumerate(document_files, 1):
            print(f"\n[{idx}/{len(document_files)}] Processing: {doc_file.name}")
            
            try:
                # Read document
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Summarize
                result = await self.summarize_document(str(doc_file), content)
                summaries.append(result)
                
                total_original_size += result['original_length']
                total_summary_size += result['summary_length']
                
                # Save summary to a separate file for reference
                summary_file = doc_file.parent / f"{doc_file.stem}_summary.txt"
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Summary of: {doc_file.name}\n")
                    f.write(f"# Original length: {result['original_length']} chars\n")
                    f.write(f"# Summary length: {result['summary_length']} chars\n")
                    f.write(f"# Compression: {result['compression_ratio']:.2%}\n\n")
                    f.write(result['summary'])
                
                print(f"  Summary saved to: {summary_file.name}")
                
            except Exception as e:
                print(f"  Error processing {doc_file.name}: {e}")
                continue
        
        # Calculate overall statistics
        avg_compression = total_summary_size / total_original_size if total_original_size > 0 else 0
        
        print("\n" + "-"*80)
        print("SUMMARIZATION COMPLETE")
        print("-"*80)
        print(f"Documents processed: {len(summaries)}")
        print(f"Total original size: {total_original_size:,} chars")
        print(f"Total summary size: {total_summary_size:,} chars")
        print(f"Overall compression: {avg_compression:.2%}")
        print(f"Space saved: {total_original_size - total_summary_size:,} chars")
        print("="*80 + "\n")
        
        return {
            "processed_count": len(summaries),
            "summaries": summaries,
            "total_original_size": total_original_size,
            "total_summary_size": total_summary_size,
            "compression_ratio": avg_compression
        }
    
    async def process(self, state: AgentState) -> AgentState:
        """
        Process state - called by workflow to summarize documents
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with summarization results
        """
        # Process documents in public_documents folder
        result = await self.process_new_documents("public_documents")
        
        # Create response message
        message = f"""Document Summarization Complete:
- Processed: {result['processed_count']} documents
- Original size: {result['total_original_size']:,} characters
- Summary size: {result['total_summary_size']:,} characters
- Compression: {result['compression_ratio']:.2%}

Documents are now ready for vector database indexing."""
        
        return {
            "messages": [HumanMessage(content=message, name="document_summarizer")],
            "next": state.get("caller", "judge"),
            "thought_step": 0,
            "caller": "document_summarizer",
            "summarization_complete": True,
            "summarization_results": result
        }
