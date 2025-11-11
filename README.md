# Lex Simulacra - AI Legal Courtroom Simulator

AI-powered legal courtroom simulator using multi-agent orchestration with LangGraph. Simulates realistic trial proceedings with defense lawyers, prosecutors, and judges using advanced RAG for accurate legal reasoning.

---

## How to Run

### Method 1: Using Batch Files (Recommended)

**First-time setup:**

```bash
setup.bat
```

Installs Python dependencies and sets up the environment.

**Launch the application:**

```bash
start_full_system.bat
```

Opens two windows:

- Backend API: http://localhost:8000
- UI Interface: http://localhost:8501

**UI-only launch** (if backend already running):

```bash
run_enhanced_ui.bat
```

### Method 2: Manual Launch

**Step 1: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 2: Start the backend**

```bash
python app.py
```

Backend runs on http://localhost:8000

**Step 3: Start the UI** (in a new terminal)

```bash
streamlit run interface\enhanced_stapp.py
```

UI runs on http://localhost:8501

### Method 3: Terminal Testing with `test_api_demo.py`

**Test via command line without UI:**

```bash
# Terminal 1: Start backend
python app.py

# Terminal 2: Run test script
python test_api_demo.py                # Uses sample_case.txt
python test_api_demo.py your_case.txt  # Uses custom case file
```

**Script Features:**

- **Color-coded output** - Different colors for each agent type
- Lawyer (Blue), Prosecutor (Red), Judge (Yellow), Verdict (Green)
- **Real-time progress tracking** - Shows iteration flow and timing
- **Live streaming** - SSE streaming from backend API
- **Full agent outputs** - Displays complete arguments and reasoning
- **Detailed summary** - Statistics at completion (iterations, time, agents)
- **Error handling** - Helpful hints if backend not running or timeouts
- **Interruptible** - Graceful handling of Ctrl+C
- **No UI needed** - Perfect for automated testing and CI/CD

---

### Using the Application (UI)

1. Open browser to **http://localhost:8501**
2. Enter case details or upload documents (sample provided)
3. Click ** Start Courtroom Simulation**
4. Watch the live trial proceedings with real-time updates

---

## Features

### Core Capabilities

- **Multi-Agent System**: Defense lawyer, prosecutor, and judge agents with distinct roles
- **Realistic Trial Flow**: Opening statements → Arguments → Rebuttals → Verdict
- **Citation Enforcement**: All legal claims must cite source documents ([IPC-1], [CAS-2])
- **Hallucination Detection**: Verifies claims against retrieved legal context
- **Real-Time UI**: Live metrics, timeline, and conversation display

### Legal Research Integration

- **Kanoon API**: Fetches relevant Indian legal cases automatically
- **Document Summarization**: Processes large legal documents efficiently
- **Web Search**: Retrieves additional legal information when needed
- **Vector Database**: ChromaDB for fast legal document retrieval

### Interactive Features

- Upload private case files (PDFs, TXT, DOCX)
- View public legal documents (IPC, case precedents)
- Real-time simulation metrics (citations, confidence, iterations)
- Timeline tracking of agent activities
- Full conversation history with formatted legal arguments

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                         │
│              (interface/enhanced_stapp.py)              │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                       │
│                    (app.py)                             │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 LangGraph Workflow                      │
│                (core/workflow.py)                       │
└─────────────────────────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ↓                ↓                ↓
    ┌────────┐      ┌──────────┐     ┌──────────┐
    │ Lawyer │      │Prosecutor│     │  Judge   │
    └────────┘      └──────────┘     └──────────┘
         │                │                │
         └────────────────┼────────────────┘
                          ↓
         ┌────────────────────────────────┐
         │   Enhanced RAG System          │
         │ (core/enhanced_rag_system.py)  │
         └────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ↓                ↓                ↓
    ┌─────────┐     ┌──────────┐    ┌──────────┐
    │ChromaDB │     │  Kanoon  │    │   Web    │
    │ Vector  │     │ API      │    │  Search  │
    │  Store  │     │          │    │          │
    └─────────┘     └──────────┘    └──────────┘
```

### Agent Workflow

```
1. Kanoon Fetcher      → Retrieves relevant Indian legal cases
2. Document Summarizer → Summarizes fetched documents
3. Initial Retriever   → Comprehensive document retrieval with RAG
4. Defense Lawyer      → Opening statement (with citations)
5. Prosecutor         → Response to defense (with citations)
6. Judge              → Evaluates arguments, routes next speaker
7. [Repeat 4-6]       → Alternating debate until conclusion
8. Verdict Agent      → Final verdict based on all arguments
```

### Key Technologies

- **LangGraph**: Multi-agent orchestration and state management
- **LangChain**: Document processing and LLM integration
- **FastAPI**: Async backend with SSE streaming
- **Streamlit**: Interactive web interface
- **ChromaDB**: Vector database for legal documents
- **Groq/OpenAI/Ollama**: LLM providers for agent reasoning

---

## Advanced RAG Techniques

### 1. Intelligent Chunking

- Detects legal structure (IPC sections, case names, numbered lists)
- Preserves section boundaries during chunking
- No mid-section cuts that lose context
- Semantic chunking with overlap for unstructured text

### 2. Citation Enforcement

- Mandatory citation format: `[IPC-1]`, `[CAS-2]`, `[EVI-1]`
- Automatic verification after each agent response
- Citation density tracking and logging
- Warnings for uncited claims

### 3. Hallucination Detection

- Extracts legal claims from agent responses
- Verifies claims against retrieved context
- Confidence scoring (e.g., "4/5 claims verified")
- Real-time warnings for unsupported arguments

### 4. Legal-Specific Re-Ranking

Document scoring by importance:

- IPC sections: 2.0x weight
- Supreme Court cases: 2.5x weight
- Case precedents: 1.8x weight
- Evidence mentions: 1.6x weight

### 5. Structured Context Presentation

Categorizes retrieved documents:

- IPC Sections
- Case Precedents
- Legal Principles
- Evidence & Facts
- Procedural Law

Each document tagged with citation markers for easy reference.

### 6. Intelligent Context Compression

- Preserves IPC mentions (5.0x importance)
- Preserves case citations (3.0x importance)
- Compresses 18K+ → 15K max while retaining key legal citations
- Extracts key points from lower-priority documents

### RAG Pipeline Flow

```
Query → Retrieval → Re-Ranking → Compression → Structuring → Verification
   ↓         ↓           ↓            ↓            ↓             ↓
Legal    Vector DB   Legal       Context      Categories    Citation
Terms    Search      Scoring     Fitting      [IPC], [CAS]  Checking
```

---

## Project Structure

```
law_courtroom_simulator/
├── agents/                    # Agent implementations
│   ├── lawyer.py             # Defense counsel
│   ├── prosecutor.py         # Prosecution
│   ├── judge.py              # Judge with routing logic
│   ├── initial_retriever.py  # Enhanced RAG retrieval
│   ├── verdict_agent.py      # Final verdict generation
│   ├── kanoon_fetcher.py     # Case law fetching
│   └── document_summarizer.py
├── core/                      # Core system components
│   ├── workflow.py           # LangGraph workflow
│   ├── enhanced_rag_system.py # Advanced RAG implementation
│   ├── chroma_store.py       # Vector database
│   └── advanced_rag.py       # Additional RAG utilities
├── interface/                 # UI components
│   └── enhanced_stapp.py     # Streamlit interface
├── public_documents/          # Legal document corpus
│   └── indian_penal_code.txt
├── private_documents/         # User-uploaded case files
├── chroma_db/                # Vector database storage
├── app.py                    # FastAPI backend
├── test_api_demo.py          # Terminal testing script (no UI needed)
├── requirements.txt          # Python dependencies
├── sample_case.txt           # Example case file
├── setup.bat                 # Automated setup
├── start_full_system.bat     # Launch script (backend + UI)
└── run_enhanced_ui.bat       # UI-only launch
```

---

## Configuration

### LLM Providers

The system supports multiple LLM providers with automatic fallback:

- Groq (default)
- OpenAI
- Ollama (local)

Configure via environment variables or modify `app.py`.

### Document Sources

- **Public**: Add legal documents to `public_documents/`
- **Private**: Upload case-specific files via UI or add to `private_documents/`
