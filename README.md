# Law Courtroom Simulator

An AI-powered legal case simulation platform that recreates authentic courtroom proceedings using multi-agent orchestration, RAG (Retrieval-Augmented Generation), and local LLMs via Ollama.

## 🎯 Overview

Law Courtroom Simulator enables users to:

- **Simulate legal proceedings** with AI agents (Judge, Lawyer, Prosecutor)
- **Test legal arguments** in a risk-free environment
- **Access legal knowledge** from IPC and precedent cases
- **Get instant feedback** on legal strategies
- **Run completely free** using local Ollama models (no API costs)

### Key Features

✅ **Multi-Agent System** - Judge, Lawyer, Prosecutor, Legal Retriever  
✅ **100% Local & Free** - Runs on Ollama (no external API costs)  
✅ **Windows Native** - Fully compatible with Windows 10/11  
✅ **Privacy First** - All data stays on your machine  
✅ **RAG-Powered** - Retrieves relevant legal documents and precedents  
✅ **Interactive UI** - Streamlit interface + REST API

---

## 🚀 Quick Start

### Prerequisites

1. **Windows 10/11** (tested on Windows 11)
2. **Python 3.9+** ([Download](https://www.python.org/downloads/))
3. **Ollama** ([Download](https://ollama.com/download/windows))
4. **15+ GB free disk space**
5. **8+ GB RAM** (16 GB recommended)

### Installation

#### 1. Install Ollama

Download and install Ollama from [ollama.com/download/windows](https://ollama.com/download/windows)

Verify installation:

```bash
ollama --version
```

#### 2. Pull Required Models

```bash
ollama pull qwen2:7b-instruct-q4_K_M
ollama pull phi3:mini
ollama pull nomic-embed-text
```

**Total size:** ~7 GB  
**Time:** 5-15 minutes depending on internet speed
**Optimized for:** RTX 4050 6GB VRAM - 5-10x faster than previous models

#### 3. Clone the Repository

```bash
git https://github.com/prasad-gade05/Law_Courtroom_Simulator
cd Law_Courtroom_Simulator
```

#### 4. Run Automated Setup

```bash
setup.bat
```

This will:

- Check Python and Ollama installation
- Create virtual environment
- Install all dependencies
- Create necessary directories
- Set up environment configuration

#### 5. Verify Setup

```bash
python verify_setup.py
```

All checks should show ✓ (green checkmarks).

---

## 📖 Usage

### Method 1: Run via API (Recommended for Testing)

#### Start the Server

```bash
# Activate virtual environment
venv\Scripts\activate

# Start FastAPI server
python app.py
```

Wait for:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Test with Sample Case

In a new terminal:

```bash
python test_api_demo.py
```

This runs a pre-configured defamation case and streams the entire workflow.

#### Or Test with Custom Case

```bash
python test_api_demo.py your_case_file.txt
```

### Method 2: Run via Streamlit UI (Interactive)

#### Start the Backend

```bash
# Terminal 1
python app.py
```

#### Start the UI

```bash
# Terminal 2
streamlit run interface/stapp.py
```

Browser opens automatically to `http://localhost:8501`

#### Use the Interface

1. **Upload Documents** - Add case files (PDF, TXT, DOCX)
2. **Enter Case Details** - Describe the legal case
3. **Start Simulation** - Click "Start Court Simulation"
4. **Provide Feedback** - Interact when prompted
5. **Review Verdict** - Read the final judgment

---

## 📁 Project Structure

```
├── app.py                      # Main FastAPI application
├── requirements.txt            # Python dependencies
├── setup.bat                   # Automated setup script
├── verify_setup.py            # Setup verification tool
├── test_api_demo.py           # API testing script
├── sample_case.txt            # Example legal case
├── .env.example               # Environment template
│
├── core/
│   ├── chroma_store.py        # Vector database (ChromaDB)
│   ├── workflow.py            # LangGraph workflow orchestration
│   └── state.py               # Agent state management
│
├── agents/
│   ├── judge.py               # Judge agent
│   ├── lawyer.py              # Defense lawyer agent
│   ├── prosecutor.py          # Prosecutor agent
│   ├── retriever.py           # Legal document retriever
│   ├── kanoon_fetcher.py      # Indian Kanoon API integration
│   └── web_search.py          # Web search agent
│
├── interface/
│   └── stapp.py               # Streamlit UI
│
├── private_documents/         # User case files (gitignored)
├── public_documents/          # Legal references (IPC, precedents)
└── chroma_db/                # Vector database storage (gitignored)
```

---

## 🎓 How to Use with Your Own Cases

### 1. Prepare Your Case File

Create a text file (e.g., `my_case.txt`) with this structure:

```text
Case File

Case Title: [Your Case Title]

Case Summary:
[Detailed description of the case, including parties involved,
allegations, date, location, and circumstances]

Case Details:
1. Date of Incident: [Date]
2. Location: [Place]
3. Nature of Offense: [Description]
4. Evidence Available: [List of evidence]

Defense Position:
1. [Your first defense argument]
2. [Your second defense argument]
3. [Additional points]

Prosecution Claims:
1. [Prosecution's main argument]
2. [Additional prosecution points]

Request:
[What you want the system to analyze - e.g., "Provide defense
strategy for this case under IPC Section XXX"]
```

### 2. Add Supporting Documents

Place any supporting documents in `private_documents/`:

- PDFs, Word documents, or text files
- Case evidence, witness statements, etc.

### 3. Run the Simulation

```bash
python test_api_demo.py my_case.txt
```

Or use the Streamlit UI to upload and interact visually.

---

## 📋 Sample Case Included

The repository includes `sample_case.txt` - a defamation and cyber harassment case:

**Case:** State vs. Rohan Malhotra  
**Charges:** Defamation (IPC 499) + Cyber Harassment (IT Act 2000)  
**Defense:** Account hacking/unauthorized access

Run it:

```bash
python test_api_demo.py sample_case.txt
```

---

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Ollama Configuration (Local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_MAIN=qwen2:7b-instruct-q4_K_M
OLLAMA_MODEL_ADVANCED=phi3:mini
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Optional External APIs
SERPER_API_KEY=your_key_here          # For web search (optional)
KANOON_API_KEY=your_key_here          # For Indian Kanoon (optional)
```

**Note:** External API keys are optional. The system works fully without them.

### Customize Models

Edit `.env` to use different Ollama models (ensure they fit your VRAM):

```env
# For higher VRAM GPUs (8GB+)
OLLAMA_MODEL_MAIN=qwen2:7b-instruct    # Full precision version
OLLAMA_MODEL_ADVANCED=llama3.1:8b      # Alternative model

# For even faster performance on 6GB VRAM
OLLAMA_MODEL_MAIN=phi3:mini            # Ultra-fast (2.3GB)
OLLAMA_MODEL_ADVANCED=gemma:2b         # Tiny but capable (1.4GB)
```

Available models: [ollama.com/library](https://ollama.com/library)

---

## 🏛️ System Architecture

### Agent Workflow

```
User Input
    ↓
┌─────────────────────────────────────┐
│ Kanoon Fetcher                      │
│ Extracts keywords & fetches cases   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Prosecutor                          │
│ Builds prosecution case             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Judge                               │
│ Reviews & requests verification     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Retriever                           │
│ Fetches relevant IPC sections       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Lawyer                              │
│ Prepares defense arguments          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ User Feedback                       │
│ Review & strengthen arguments       │
└─────────────────────────────────────┘
    ↓
[Cycle repeats 5-10 times]
    ↓
┌─────────────────────────────────────┐
│ Judge Final Verdict                 │
│ Delivers judgment with reasoning    │
└─────────────────────────────────────┘
```

### Technology Stack

- **LLM Framework:** LangChain + LangGraph
- **Vector Database:** ChromaDB
- **Local LLM:** Ollama (llama3.1, mistral)
- **Embeddings:** nomic-embed-text
- **API Framework:** FastAPI
- **UI Framework:** Streamlit
- **Document Processing:** PyMuPDF, python-docx

---

## ⏱️ Performance & Timing

### First Run (Cold Start)

- **Document Indexing:** 2-5 minutes
- **Model Loading:** 1-2 minutes
- **First Workflow:** 15-30 minutes

### Subsequent Runs (Warm Start)

- **Model Loading:** < 30 seconds
- **Workflow Execution:** 10-20 minutes

### Factors Affecting Speed

- **CPU/GPU:** Faster hardware = faster inference
- **Model Size:** Smaller models (7-8B) faster than large (70B)
- **Document Count:** More documents = longer indexing
- **Case Complexity:** Complex cases need more iterations

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError"

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. "Ollama not running"

```bash
# Start Ollama
ollama serve

# Verify it's running
curl http://localhost:11434
```

#### 3. "Model not found"

```bash
# Check installed models
ollama list

# Pull missing model
ollama pull llama3.1:8b
```

#### 4. "Port 8000 already in use"

```bash
# Find and kill the process
netstat -ano | findstr :8000
taskkill /F /PID <process_id>
```

#### 5. "ChromaDB initialization slow"

- **Normal on first run** - Generating embeddings takes time
- Watch the progress bar - it shows real-time status
- For 96 chunks (typical): 2-4 minutes

#### 6. "No verdict given"

- Workflows need 8-10 argument rounds minimum
- Continue providing feedback when prompted
- Be patient - complex cases take longer

### Get More Help

1. Run diagnostics: `python verify_setup.py`
2. Check console logs for detailed errors
3. Ensure Ollama models are loaded: `ollama list`

---

## 📊 System Requirements

### Minimum

- **OS:** Windows 10 (64-bit)
- **CPU:** 4 cores
- **RAM:** 8 GB
- **Storage:** 15 GB free
- **Internet:** Required for initial setup only

### Recommended

- **OS:** Windows 11 (64-bit)
- **CPU:** 8+ cores
- **RAM:** 16 GB
- **GPU:** NVIDIA GPU with 8GB+ VRAM (optional, for faster inference)
- **Storage:** 20 GB+ free

### Notes

- **GPU acceleration** is automatic if NVIDIA GPU detected
- **CPU-only mode** works but slower
- **First run** requires internet for downloading models

---

## 🔒 Privacy & Security

- ✅ **All processing happens locally** - No data sent to external servers
- ✅ **No API keys required** - Fully functional without external APIs
- ✅ **Your documents stay private** - Never leave your machine
- ✅ **Open source** - Inspect the code yourself

Optional external APIs (if configured):

- **Serper API** - Web search only
- **Kanoon API** - Legal case database access only

---

## 📦 Dependencies

Main packages (see `requirements.txt` for full list):

- `langchain` - LLM framework
- `langgraph` - Workflow orchestration
- `chromadb` - Vector database
- `ollama` - Local LLM client
- `fastapi` - REST API
- `streamlit` - Web UI
- `pymupdf` - PDF processing
- `python-docx` - Word document processing

---
