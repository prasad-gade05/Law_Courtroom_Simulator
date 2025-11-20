"""
ChromaDB Vector Store - Ollama embeddings
"""
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from core.enhanced_rag_system import IntelligentChunker
from pathlib import Path
import time
from typing import Optional
import os
import re
from dotenv import load_dotenv

load_dotenv()


class ChromaVectorStore:
    """
    Vector store using ChromaDB with local Ollama embeddings.
    
    Parameters:
        name: Name for the database collection (e.g., 'public', 'private')
        path: Path to directory containing documents to index
        embedding_model: Ollama embedding model name (default: 'nomic-embed-text')
    """
    
    def __init__(
        self, 
        name: str, 
        path: str,
        embedding_model: str = None,
        persist_directory: Optional[str] = None,
        skip_indexing: bool = False
    ):
        self.name = name
        self.path = path
        
        # Get embedding model from env or use default for Ollama
        if embedding_model is None:
            embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        self.embedding_model = embedding_model
        
        # Set persistence directory
        if persist_directory is None:
            persist_directory = f"./chroma_db/{name}"
        self.persist_directory = persist_directory
        
        # Ensure persist directory exists
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Enable WAL mode on SQLite database to prevent concurrent write lock contention
        db_file = Path(self.persist_directory) / "chroma.sqlite3"
        import sqlite3
        try:
            conn = sqlite3.connect(str(db_file))
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.close()
        except Exception as e:
            pass
        
        print(f"\n{'='*60}")
        print(f"Initializing ChromaVectorStore: '{self.name}'")
        print(f"{'='*60}")
        print(f"Documents path: {self.path}")
        print(f"Persist directory: {self.persist_directory}")
        print(f"Embedding model: {self.embedding_model}")
        print()
        
        try:
            # Initialize Ollama embeddings
            print(f"Initializing Ollama embeddings...", end='', flush=True)
            self.embeddings = OllamaEmbeddings(model=self.embedding_model)
            print(" [OK]")
            
            # Initialize custom legal text chunker
            print(f"Initializing Intelligent Chunker (chunk_size=1000, overlap=200)...", end='', flush=True)
            self.chunker = IntelligentChunker(chunk_size=1000, chunk_overlap=200)
            print(" [OK]")
            
            # Initialize ChromaDB client with persistence
            print(f"Initializing ChromaDB client...", end='', flush=True)
            self.chroma_client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            print(" [OK]")
            
            # Create or get collection
            self.collection_name = f"{name}_collection"
            
            # Initialize vector store
            print(f"Initializing vector store collection '{self.collection_name}'...", end='', flush=True)
            self.vectorstore = Chroma(
                client=self.chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )
            print(" [OK]")
            
            # Check if collection already has data (skip re-indexing)
            existing_count = self.vectorstore._collection.count()
            if existing_count > 0:
                print(f"\n[CACHE] Found existing vector store with {existing_count} embeddings")
                print(f"[CACHE] Skipping re-indexing (data already cached)")
                print(f"   Delete '{self.persist_directory}' folder to force re-indexing")
            elif not skip_indexing:
                print(f"\n[NEW] No existing data found - will index documents")
                # Process and index documents from path
                self._index_documents()
            else:
                print(f"\n[NEW] No existing data found - skipping indexing as requested")
            
            print(f"\nChromaVectorStore '{self.name}' initialized successfully!")
            print(f"{'='*60}\n")
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ChromaVectorStore: {str(e)}")

    def reset_collection(self):
        """
        Safely reset/clear the vector store collection.
        This deletes the existing collection programmatically to trigger re-indexing
        on next initialization, avoiding unsafe manual folder deletion issues.
        """
        try:
            print(f"Resetting vector store collection '{self.collection_name}'...", end='', flush=True)
            self.chroma_client.delete_collection(self.collection_name)
            # Recreate vectorstore wrapper to make sure it's initialized on the clean empty database
            self.vectorstore = Chroma(
                client=self.chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )
            print(" [OK]")
        except Exception as e:
            print(f" [FAILED] Error: {e}")

    def _index_documents(self):
        """
        Index all documents from the specified path into ChromaDB.
        Prioritizes summarized versions (*_summary.txt) over original documents.
        Supports .txt, .pdf, .docx files.
        """
        from pathlib import Path
        import os
        import sys
        
        doc_path = Path(self.path)
        
        if not doc_path.exists():
            print(f"[WARNING] Document path '{self.path}' does not exist. Creating empty store.")
            return
        
        # Get all supported document files
        supported_extensions = ['.txt', '.pdf', '.docx', '.doc']
        document_files = []
        
        print(f"Scanning for documents in '{self.path}'...")
        for ext in supported_extensions:
            found = list(doc_path.glob(f'**/*{ext}'))
            if found:
                print(f"   Found {len(found)} {ext} file(s)")
            document_files.extend(found)
        
        if not document_files:
            print(f"[WARNING] No documents found in '{self.path}'. Store will be empty.")
            return
        
        # Filter: Prioritize summary files, skip original if summary exists
        filtered_files = []
        summary_bases = set()
        
        # First pass: identify all summary files
        for doc_file in document_files:
            if '_summary.txt' in doc_file.name:
                # Extract base name (e.g., "doc_summary.txt" -> "doc")
                base_name = doc_file.name.replace('_summary.txt', '.txt')
                summary_bases.add(base_name)
                filtered_files.append(doc_file)
        
        # Second pass: add non-summary files if no summary exists
        for doc_file in document_files:
            if '_summary.txt' not in doc_file.name:
                if doc_file.name not in summary_bases:
                    filtered_files.append(doc_file)
                else:
                    print(f"   Skipping {doc_file.name} (using summary instead)")
        
        document_files = filtered_files
        
        print(f"\nTotal documents to process: {len(document_files)}")
        print("=" * 60)
        
        # Process each document
        all_texts = []
        all_metadatas = []
        
        for doc_idx, doc_file in enumerate(document_files, 1):
            try:
                is_summary = '_summary.txt' in doc_file.name
                doc_type = "SUMMARY" if is_summary else "FULL"
                
                print(f"\n[{doc_idx}/{len(document_files)}] Processing: {doc_file.name} [{doc_type}]")
                print(f"   Reading file...", end='', flush=True)
                
                text = self._extract_text(doc_file)
                print(f" [OK] ({len(text)} characters)")
                
                if text.strip():
                    # Split into chunks using custom IntelligentChunker
                    print(f"   Splitting into chunks using IntelligentChunker...", end='', flush=True)
                    chunk_docs = self.chunker.chunk_document(text, metadata={
                        "source": str(doc_file),
                        "filename": doc_file.name
                    })
                    print(f" [OK] ({len(chunk_docs)} chunks)")
                    
                    # Create metadata for each chunk with enhanced information
                    print(f"   Creating metadata...", end='', flush=True)
                    for i, doc in enumerate(chunk_docs):
                        all_texts.append(doc.page_content)
                        
                        # Enhanced metadata for better retrieval, merging chunker metadata (like section_header)
                        metadata = {
                            **doc.metadata,
                            "chunk_index": i,
                            "total_chunks": len(chunk_docs),
                            "chunk_size": len(doc.page_content),
                            "document_type": self._infer_document_type(doc_file.name, doc.page_content),
                        }
                        
                        # Extract key entities from chunk (IPC sections, case names, etc.)
                        entities = self._extract_legal_entities(doc.page_content)
                        if entities:
                            metadata["legal_entities"] = ", ".join(entities)
                        
                        all_metadatas.append(metadata)
                    print(f" [OK]")
                else:
                    print(f"   [WARNING] File is empty or unreadable")
                
            except Exception as e:
                print(f"\n   [ERROR] processing {doc_file.name}: {e}")
                continue
        
        # Add all documents to vector store
        if all_texts:
            print("\n" + "=" * 60)
            print(f"Generating embeddings and indexing {len(all_texts)} chunks...")
            print(f"   Using Ollama embeddings ({self.embedding_model})")
            print(f"   This may take a few minutes...")
            print(f"   Progress: ", end='', flush=True)
            
            # Index in batches to show progress
            batch_size = 10
            total_batches = (len(all_texts) + batch_size - 1) // batch_size
            
            for i in range(0, len(all_texts), batch_size):
                batch_texts = all_texts[i:i+batch_size]
                batch_metadatas = all_metadatas[i:i+batch_size]
                
                self.vectorstore.add_texts(
                    texts=batch_texts,
                    metadatas=batch_metadatas
                )
                
                current_batch = (i // batch_size) + 1
                progress_pct = (current_batch / total_batches) * 100
                
                # Visual progress bar
                bar_length = 40
                filled = int(bar_length * current_batch / total_batches)
                bar = '#' * filled + '-' * (bar_length - filled)
                
                print(f"\r   Progress: [{bar}] {progress_pct:.1f}% ({i+len(batch_texts)}/{len(all_texts)} chunks)", 
                      end='', flush=True)
            
            print()  # New line after progress bar
            print(f"Successfully indexed {len(all_texts)} chunks from {len(document_files)} documents")
            print("=" * 60)
        else:
            print("\n[WARNING] No text content extracted from documents.")

    # ... (the rest of the file remains the same) ...

    def _extract_text(self, file_path: Path) -> str:
        """
        Extract text from various file formats.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text content
        """
        extension = file_path.suffix.lower()
        
        if extension == '.txt':
            return self._extract_from_txt(file_path)
        elif extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def _extract_from_txt(self, file_path: Path) -> str:
        """Extract text from .txt file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except:
                    continue
            raise ValueError(f"Could not decode {file_path} with any encoding")
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            raise ImportError("PyMuPDF (fitz) is required for PDF processing. Install with: pip install pymupdf")
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from Word documents"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except ImportError:
            raise ImportError("python-docx is required for Word document processing. Install with: pip install python-docx")
    
    def get_client(self):
        """
        Get the vector store for retrieval operations.
        Returns a retriever that's compatible with the old PathwayVectorClient interface.
        
        Returns:
            Chroma vectorstore instance that can be used as a retriever
        """
        return self.vectorstore
    
    def similarity_search(self, query: str, k: int = 4):
        """
        Perform similarity search on the vector store.
        
        Args:
            query: Search query text
            k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        return self.vectorstore.similarity_search(query, k=k)
    
    def as_retriever(self, **kwargs):
        """
        Get a retriever interface for the vector store.
        Compatible with LangChain's retriever interface.
        
        Returns:
            LangChain retriever object
        """
        # Set better default retrieval parameters
        default_kwargs = {
            "search_type": "mmr",  # Maximum Marginal Relevance for diversity
            "search_kwargs": {
                "k": 10,  # Retrieve more initially for re-ranking
                "fetch_k": 20,  # Fetch even more for MMR
                "lambda_mult": 0.7  # Balance between relevance and diversity
            }
        }
        default_kwargs.update(kwargs)
        return self.vectorstore.as_retriever(**default_kwargs)
    
    def _infer_document_type(self, filename: str, content: str) -> str:
        """Infer document type from filename and content"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Check filename patterns
        if "ipc" in filename_lower or "penal code" in filename_lower:
            return "penal_code"
        elif "case" in filename_lower or "judgment" in filename_lower:
            return "case_law"
        elif "crpc" in filename_lower or "procedure" in filename_lower:
            return "procedural_law"
        elif "evidence" in filename_lower:
            return "evidence_act"
        
        # Check content patterns
        if "section" in content_lower and "ipc" in content_lower:
            return "penal_code"
        elif "v." in content_lower or "vs." in content_lower:
            return "case_law"
        elif "supreme court" in content_lower or "high court" in content_lower:
            return "case_law"
        
        return "general_legal"
    
    def _extract_legal_entities(self, text: str) -> list:
        """Extract legal entities like IPC sections, case names, etc."""
        entities = []
        
        # Extract IPC sections
        ipc_pattern = r'(?:IPC\s+)?[Ss]ection\s+(\d+[A-Z]?)'
        ipc_matches = re.findall(ipc_pattern, text)
        entities.extend([f"IPC {match}" for match in ipc_matches[:3]])  # Limit to 3
        
        # Extract case names (simplified pattern)
        case_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v[s]?\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        case_matches = re.findall(case_pattern, text)
        entities.extend([f"{plaintiff} v. {defendant}" for plaintiff, defendant in case_matches[:2]])
        
        return entities[:5]  # Limit total entities


if __name__ == "__main__":
    # Example/test usage
    print("Testing ChromaVectorStore...")
    
    # Test with public documents
    public_db = ChromaVectorStore('test_public', './public_documents')
    
    print('\nMaking a test query...')
    result = public_db.as_retriever().invoke("IPC 345")
    
    print(f"\nFound {len(result)} results:")
    for i, doc in enumerate(result, 1):
        # Safe print for different terminal encodings (e.g. Windows cp1252)
        safe_content = doc.page_content[:200].encode('ascii', errors='replace').decode('ascii')
        print(f"Content: {safe_content}...")
        print(f"Metadata: {doc.metadata}")