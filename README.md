# PathRAG Court Simulator ⚖️

An AI-powered legal courtroom simulator using multi-agent orchestration and Google Gemini AI. Experience realistic trial proceedings with intelligent agents representing judges, lawyers, and prosecutors.

## Features

- **Multi-Agent System** - Judge, Defense Lawyer, Prosecutor, Legal Researcher, and Web Searcher working together
- **Fast & Efficient** - Google Gemini 2.5 Flash provides quick responses (~5-8 minutes per trial)
- **Cloud-Based** - No GPU required, runs entirely on cloud infrastructure
- **RAG Integration** - Retrieval-Augmented Generation for accurate legal research
- **Real-Time Streaming** - Watch the trial unfold with live updates
- **Fair Proceedings** - Both prosecution and defense get equal speaking opportunities
- **Guaranteed Verdict** - Maximum 25 iterations with forced verdict delivery

---

## Getting Started

### Prerequisites

Before you begin, ensure you have:

- **Windows 10/11** (or Linux/macOS with minor script adjustments)
- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
- **Google AI API Key** (free) - [Get API Key](https://aistudio.google.com/app/apikey)
- **8+ GB RAM** (16 GB recommended)
- **Internet connection** (required for cloud API)

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

- FastAPI (API framework)
- LangChain (LLM orchestration)
- LangGraph (Agent workflow)
- Google Generative AI (Gemini)
- ChromaDB (Vector database)
- Streamlit (Web UI)
- And other required packages

### Step 4: Configure API Key

1. **Get your Google AI API key:**

   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the key (format: `AIzaSy...`)

2. **Create environment file:**

   ```bash
   # Windows
   copy .env.example .env

   # Linux/macOS
   cp .env.example .env
   ```

3. **Add your API key:**

   Open `.env` in a text editor and add:

   ```env

    GOOGLE_API_KEY=YOUR_API_KEY

    GEMINI_MODEL=gemini-2.5-flash-lite
    GEMINI_EMBEDDING_MODEL=text-embedding-004


    SERPER_API_KEY=YOUR_API_KEY
    KANOON_API_KEY=YOUR_API_KEY

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

Edit `.env` file:

```env
# Required
GOOGLE_API_KEY=your_api_key_here

# Model Selection
GEMINI_MODEL=gemini-2.5-flash-lite

# External APIs
SERPER_API_KEY=YOUR_KEY                      # For web search
KANOON_API_KEY=YOUR_KEY                      # For Indian case law
```

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

- **👨‍⚖️ Judge** - Controls trial flow, evaluates arguments, delivers verdict
- **🛡️ Defense Lawyer** - Builds defense, finds weaknesses in prosecution
- **⚔️ Prosecutor** - Presents charges, challenges defense claims
- **📚 Legal Retriever** - Searches legal documents and precedents
- **🔍 Kanoon Fetcher** - Finds similar cases from Indian Kanoon database
- **🌐 Web Searcher** - Searches internet for additional legal information

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
