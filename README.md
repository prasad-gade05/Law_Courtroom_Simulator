# PathRAG Court Simulator ⚖️

An AI-powered legal courtroom simulator using multi-agent orchestration with LangGraph. Experience realistic trial proceedings with intelligent agents representing judges, lawyers, and prosecutors debating real legal cases.

## Features

- **Multi-Agent System** - Judge, Defense Lawyer, Prosecutor, Legal Researcher, Kanoon Fetcher, and Web Searcher working together
- **Local & Cloud Options** - Works with Ollama (local LLM) or Google Gemini AI
- **Robust Workflow** - LangGraph-based orchestration ensures guaranteed verdict delivery
- **RAG Integration** - Retrieval-Augmented Generation for accurate legal research
- **Real-Time Streaming** - Watch the trial unfold with live updates
- **Fair Proceedings** - Both prosecution and defense get equal speaking opportunities
- **Guaranteed Verdict** - Multi-layer safety mechanisms ensure verdict is always delivered (max 40 iterations)
- **Smart Debating** - Automatic debate conclusion when arguments are exhausted

---

## Getting Started

### Prerequisites

Before you begin, ensure you have:

- **Windows 10/11, Linux, or macOS**
- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
- **LLM Setup (Choose one)**:
  - **Option A**: Ollama with a compatible model (local, recommended)
    ```bash
    # Install Ollama from https://ollama.ai/
    ollama pull llama3:8b  # or your preferred model
    ```
  - **Option B**: Google AI API Key (free) - [Get API Key](https://aistudio.google.com/app/apikey)
- **8+ GB RAM** (16 GB recommended)
- **Internet connection** (required for APIs and legal data retrieval)

### Step 1: Clone the Repository

```bash
git clone https://github.com/prasad-gade05/Law_Courtroom_Simulator
cd Law_Courtroom_Simulator
```

### Step 2: Set Up Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**

```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:

- **FastAPI** - API framework
- **LangChain & LangGraph** - Multi-agent orchestration
- **LangChain Google GenAI** - Google Gemini integration
- **LangChain Ollama** - Local LLM support
- **ChromaDB** - Vector database
- **Streamlit** - Web UI
- **CrewAI** - Web search capabilities
- **Rich** - Terminal formatting
- And other required packages

### Step 4: Configure Environment

**Create environment file:**

```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

**Configure your LLM:**

Choose ONE of the following options:

**Option A - Ollama (Local, Recommended):**
```env
OLLAMA_MODEL=llama3:8b
# Or: gpt-oss:120b-cloud, mistral:7b, etc.
```

**Option B - Google Gemini:**
```env
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
GEMINI_MODEL=gemini-2.5-flash-lite
GEMINI_EMBEDDING_MODEL=text-embedding-004
```

**Optional - Additional APIs:**
```env
SERPER_API_KEY=YOUR_SERPER_KEY       # For web search (optional)
KANOON_API_KEY=YOUR_KANOON_KEY       # For Indian case law (optional)
```

### Step 5: Verify Setup

```bash
python verify_setup.py
```

**Expected output:**

```
✓ Python version: 3.x.x
✓ Virtual environment: Active
✓ Dependencies: Installed
✓ Google API Key: Valid
✓ All checks passed!
```

### Step 6: Run the Application

**Option A: API Mode (Recommended for testing)**

Terminal 1 - Start the backend server:

```bash
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/macOS

python app.py
```

Wait for:

```
INFO: Uvicorn running on http://0.0.0.0:8000
All agents initialized successfully
```

Terminal 2 - Run a test case:

```bash
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/macOS

python test_api_demo.py
```

**Option B: Web Interface**

Terminal 1 - Start backend:

```bash
python app.py
```

Terminal 2 - Start web UI:

```bash
streamlit run interface/stapp.py
```

Browser will open automatically at `http://localhost:8501`

---

## Usage

### Running Sample Case

The project includes a sample defamation case:

```bash
python test_api_demo.py sample_case.txt
```

### Creating Your Own Case

Create a text file with this format:

```text
Case Title: State vs. [Defendant Name]

Case Summary:
[Detailed description of what happened, who is involved, dates, location]

Case Details:
1. Date of Incident: [Date]
2. Nature of Offense: [Crime/Issue]
3. Evidence: [List of evidence]
4. Parties:
   - Accused: [Name, age, occupation]
   - Victim: [Name, age, occupation]

Defense Position:
1. [Main defense argument]
2. [Supporting evidence]
3. [Legal precedents]

Prosecution Claims:
1. [Charges]
2. [Evidence against accused]
3. [Witness statements]

Request:
[What legal analysis you need]
```

Then run:

```bash
python test_api_demo.py your_case.txt
```

### Expected Output

You'll see real-time streaming of the trial:

```
================================================================================
⚔️ PROSECUTOR - Iteration 2
================================================================================
[Prosecutor's opening statement and charges...]

================================================================================
🛡️ LAWYER - Iteration 4
================================================================================
[Defense arguments and counterpoints...]

================================================================================
⚖️ JUDGE - Iteration 20
================================================================================
[Judge's analysis and reasoning...]

================================================================================
🏛️ FINAL VERDICT
================================================================================
VERDICT DELIVERED: After careful consideration of all arguments...
[Detailed verdict with legal reasoning]
```

---

## Project Structure

```
Inter-IIT-Pathway-PathRAG-Court-Simulator/
│
├── app.py                    # FastAPI backend server
├── test_api_demo.py         # API testing script
├── sample_case.txt          # Example case file
├── requirements.txt         # Python dependencies
├── verify_setup.py          # Setup verification tool
├── .env                     # Your configuration (create this)
├── .env.example            # Configuration template
│
├── agents/                  # AI agent implementations
│   ├── judge.py            # Judge agent
│   ├── lawyer.py           # Defense lawyer agent
│   ├── prosecutor.py       # Prosecutor agent
│   ├── retriever.py        # Legal document retriever
│   ├── kanoon_fetcher.py   # Case law fetcher
│   └── web_search.py       # Web search agent
│
├── core/                    # Core system components
│   ├── workflow.py         # LangGraph workflow orchestration
│   ├── state.py            # Agent state management
│   └── chroma_store.py     # Vector database interface
│
├── interface/              # User interfaces
│   └── stapp.py           # Streamlit web UI
│
├── private_documents/      # Your case documents (gitignored)
├── public_documents/       # Legal reference documents
└── chroma_db/             # Vector database cache (gitignored)
```

---

## Configuration

### Environment Variables

Edit `.env` file based on your chosen LLM:

```env
# For Ollama (Local)
OLLAMA_MODEL=llama3:8b

# OR For Google Gemini
GOOGLE_API_KEY=your_google_api_key
GEMINI_MODEL=gemini-2.5-flash-lite
GEMINI_EMBEDDING_MODEL=text-embedding-004

# Optional APIs
SERPER_API_KEY=your_serper_key       # For web search
KANOON_API_KEY=your_kanoon_key       # For Indian case law
```

### Verdict Guarantee Mechanism

The simulator uses multiple safety layers to ensure a verdict is always delivered:

1. **Iteration 16**: Router starts winding down debate
2. **Iteration 18**: Judge automatically forces verdict (normal path)
3. **Iteration 22**: Emergency verdict safety net (if needed)
4. **Fallback**: LLM-based analysis verdict if all else fails

This ensures you'll **always** get a verdict, even if the workflow encounters issues.

## How It Works

### Agent Workflow

```
1. User submits case
    ↓
2. Kanoon Fetcher finds similar cases
    ↓
3. Prosecutor builds charges
    ↓
4. Judge reviews and requests legal research
    ↓
5. Legal Retriever fetches relevant laws
    ↓
6. Defense Lawyer counters with arguments
    ↓
7. Judge evaluates both sides
    ↓
8. [Cycle repeats with rebuttals]
    ↓
9. Judge delivers final verdict
```

### Key Agents

- **👨‍⚖️ Judge** - Controls trial flow, evaluates arguments, ensures fair proceedings, delivers verdict
- **🛡️ Defense Lawyer** - Builds defense arguments, challenges prosecution, cites legal precedents
- **⚔️ Prosecutor** - Presents charges, builds case against defendant, rebuts defense claims
- **📚 Legal Retriever** - Searches ChromaDB vector database for relevant legal documents
- **🔍 Kanoon Fetcher** - Finds similar cases from Indian Kanoon database
- **🌐 Web Searcher** - Searches internet for additional legal information and precedents
- **🏛️ Verdict Agent** - Generates final verdict based on complete trial transcript

### Technologies Used

- **LangGraph** - Multi-agent workflow orchestration
- **LangChain** - LLM abstraction and tooling
- **ChromaDB** - Vector database for legal document storage
- **FastAPI** - REST API backend
- **Streamlit** - Web-based user interface
- **CrewAI** - Agent framework for web search
- **Ollama/Google Gemini** - Large language models

---

## Troubleshooting

### Issue: "Recursion limit reached"

**Solution**: The simulator has built-in safety mechanisms. If you see this error, the emergency verdict should have been delivered. Check the last output messages for the verdict.

### Issue: "Ollama connection failed"

**Solution**: Ensure Ollama is installed and running:
```bash
# Start Ollama service
ollama serve

# Test connection
ollama list
```

### Issue: "No verdict displayed"

**Solution**: The verdict is guaranteed to be delivered. Check:
1. Look for "🏛️ FINAL VERDICT" header in output
2. Check for "VERDICT DELIVERED:" in the message
3. Verdict is shown at iteration 18-22 range

---

## API Reference

### POST `/stream_workflow`

Stream trial workflow in real-time.

**Request:**

```json
{
  "user_prompt": "Your case description here"
}
```

**Response:** Server-Sent Events (SSE) stream

**Example:**

```python
import requests

url = "http://localhost:8000/stream_workflow"
data = {"user_prompt": "Your case here"}

response = requests.post(url, json=data, stream=True)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

---
