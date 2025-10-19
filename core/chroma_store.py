"""
ChromaDB Vector Store - Cloud-ready with Google Gemini embeddings
"""
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
import time
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class ChromaVectorStore:
    """
    Vector store using ChromaDB with Google Gemini embeddings.
    Cloud-based embeddings for better performance and no local GPU requirement.
    
    Parameters:
        name: Name for the database collection (e.g., 'public', 'private')
        path: Path to directory containing documents to index
        embedding_model: Google embedding model name (default: 'models/text-embedding-004')
    """
    
    def __init__(
        self, 
        name: str, 
        path: str,
        embedding_model: str = None,
        persist_directory: Optional[str] = None
    ):
        self.name = name
        self.path = path
        
        # Get embedding model from env or use default
        if embedding_model is None:
            embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
        self.embedding_model = embedding_model
        
        # Ensure model name doesn't have models/ prefix (LiteLLM compatibility)
        if self.embedding_model.startswith("models/"):
            self.embedding_model = self.embedding_model.replace("models/", "")
        
        # Set persistence directory
        if persist_directory is None:
            persist_directory = f"./chroma_db/{name}"
        self.persist_directory = persist_directory
        
        # Ensure persist directory exists
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"Initializing ChromaVectorStore: '{self.name}'")
        print(f"{'='*60}")
        print(f"Documents path: {self.path}")
        print(f"Persist directory: {self.persist_directory}")
        print(f"Embedding model: {self.embedding_model}")
        print()
        
        try:
            # Initialize Google Gemini embeddings
            print(f"Initializing Google Gemini embeddings...", end='', flush=True)
            google_api_key = os.getenv("GOOGLE_API_KEY")
            if not google_api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
            # GoogleGenerativeAIEmbeddings expects models/ prefix
            embedding_model_with_prefix = f"models/{self.embedding_model}" if not self.embedding_model.startswith("models/") else self.embedding_model
            
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=embedding_model_with_prefix,
                google_api_key=google_api_key
            )
            print(" [OK]")
            
            # Initialize text splitter
            print(f"Initializing text splitter (chunk_size=5000)...", end='', flush=True)
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=5000,
                chunk_overlap=10,
                length_function=len,
            )
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
            else:
                print(f"\n[NEW] No existing data found - will index documents")
                # Process and index documents from path
                self._index_documents()
            
            print(f"\nChromaVectorStore '{self.name}' initialized successfully!")
            print(f"{'='*60}\n")
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ChromaVectorStore: {str(e)}")
    
    def _index_documents(self):
        """
        Index all documents from the specified path into ChromaDB.
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
        
        print(f"\nTotal documents to process: {len(document_files)}")
        print("=" * 60)
        
        # Process each document
        all_texts = []
        all_metadatas = []
        
        for doc_idx, doc_file in enumerate(document_files, 1):
            try:
                print(f"\n[{doc_idx}/{len(document_files)}] Processing: {doc_file.name}")
                print(f"   Reading file...", end='', flush=True)
                
                text = self._extract_text(doc_file)
                print(f" [OK] ({len(text)} characters)")
                
                if text.strip():
                    # Split into chunks
                    print(f"   Splitting into chunks...", end='', flush=True)
                    chunks = self.text_splitter.split_text(text)
                    print(f" [OK] ({len(chunks)} chunks)")
                    
                    # Create metadata for each chunk
                    print(f"   Creating metadata...", end='', flush=True)
                    for i, chunk in enumerate(chunks):
                        all_texts.append(chunk)
                        all_metadatas.append({
                            "source": str(doc_file),
                            "filename": doc_file.name,
                            "chunk_index": i,
                            "total_chunks": len(chunks)
                        })
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
            print(f"   Using Google Gemini API (cloud-based)")
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
        return self.vectorstore.as_retriever(**kwargs)


if __name__ == "__main__":
    # Example/test usage
    print("Testing ChromaVectorStore...")
    
    # Test with public documents
    public_db = ChromaVectorStore('test_public', './public_documents')
    
    print('\nMaking a test query...')
    result = public_db.as_retriever().invoke("IPC 345")
    
    print(f"\nFound {len(result)} results:")
    for i, doc in enumerate(result, 1):
        print(f"\n--- Result {i} ---")
        print(f"Content: {doc.page_content[:200]}...")
        print(f"Metadata: {doc.metadata}")
