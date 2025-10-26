# Lex Simulacra - Law Courtroom Simulator

An AI-powered legal courtroom simulator that uses multi-agent orchestration with LangGraph to conduct realistic trial proceedings. The system simulates a complete courtroom environment where AI agents representing judges, defense lawyers, and prosecutors debate legal cases using real legal frameworks.

## Getting Started

### Option 1: Automated Setup (Recommended for Windows)

Run the automated setup script that handles all installation steps:

```bash
setup.bat
```

The script will automatically:
- Create a virtual environment
- Install all required Python packages
- Download necessary Ollama models (nomic-embed-text, gpt-oss:120b-cloud)
- Create configuration directories
- Set up your .env file
- Verify the installation

### Option 2: Manual Setup

**Step 1: Create Virtual Environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

**Step 2: Install Dependencies**

```bash
pip install -r requirements.txt
```

**Step 3: Install and Configure Ollama**

Download and install Ollama from https://ollama.com/download

Pull required models:
```bash
ollama pull nomic-embed-text
ollama pull gpt-oss:120b-cloud
```

Verify Ollama is running:
```bash
ollama list
```

**Step 4: Create Environment Configuration**

Create a `.env` file in the project root with the following configuration:

```env
# Ollama Configuration
OLLAMA_MODEL=gpt-oss:120b-cloud

# External APIs
SERPER_API_KEY=your_serper_api_key
KANOON_API_KEY=your_kanoon_api_key
```

**Step 5: Create Required Directories**

```bash
mkdir private_documents
mkdir public_documents
mkdir chroma_db
```

**Step 6: Verify Setup**

```bash
python verify_setup.py
```

### Running the Application

**Start the Backend Server:**

```bash
python app.py
```

Wait for the message: `All agents initialized successfully`

**Run a Test Case:**

In a separate terminal:
```bash
python test_api_demo.py sample_case.txt
```

## Environment Configuration

Create a `.env` file with these required variables:

```env
# Ollama Configuration
OLLAMA_MODEL=gpt-oss:120b-cloud

# External APIs
SERPER_API_KEY=your_serper_api_key
KANOON_API_KEY=your_kanoon_api_key
```

Configuration details:
- **OLLAMA_MODEL**: The primary LLM model for all agents. Default is gpt-oss:120b-cloud. Alternative options include llama3:8b, mistral:7b, or other Ollama-compatible models.
- **SERPER_API_KEY**: API key for web search functionality. Obtain from https://serper.dev (optional but recommended for comprehensive legal research).
- **KANOON_API_KEY**: API key for accessing Indian case law database through Indian Kanoon. Required for fetching precedent cases.

## System Architecture

### Multi-Agent Workflow

The system implements a sophisticated multi-agent workflow orchestrated by LangGraph. The trial proceeds through structured phases with agents communicating through a shared state management system.

**Workflow Sequence:**

1. **Case Initialization**: User submits case details through the API endpoint
2. **Precedent Research**: Kanoon Fetcher agent searches for similar historical cases
3. **Prosecution Opening**: Prosecutor agent analyzes the case and formulates charges
4. **Judicial Review**: Judge agent evaluates prosecution claims and directs proceedings
5. **Legal Research**: Retriever agent queries the vector database for relevant laws and statutes
6. **Defense Arguments**: Lawyer agent constructs defense based on legal research and case facts
7. **Iterative Debate**: Judge facilitates alternating arguments between prosecution and defense
8. **Verdict Generation**: Verdict agent synthesizes all arguments and delivers final judgment

### Agent Descriptions

**Judge Agent**

The Judge agent serves as the central orchestrator of the trial workflow. It evaluates arguments from both sides for logical consistency, factual accuracy, and legal soundness. The judge maintains fairness by ensuring equal speaking opportunities for prosecution and defense. It actively monitors the proceedings to detect argument exhaustion or repetition, and has the authority to conclude debates when natural completion is reached. The judge does not conduct research but relies on its legal knowledge to provide feedback and corrections to other agents.

**Defense Lawyer Agent**

The Lawyer agent represents the defendant and builds comprehensive defense strategies. It follows a structured chain of thought process: reviewing case details, identifying required legal information, requesting data from the retriever agent, assessing need for web-based research, and constructing persuasive arguments. The lawyer actively counters prosecution claims using legal precedents, statutes, and factual evidence. It responds to judicial feedback by refining arguments while maintaining the client's position. The agent prioritizes local database searches before requesting web-based information.

**Prosecutor Agent**

The Prosecutor agent advocates for the opposing party by challenging defense arguments and presenting evidence. It analyzes the case to identify weaknesses in defense claims and formulates charges based on applicable laws. The prosecutor follows the same information-gathering protocol as the lawyer, first consulting the retriever agent and then requesting web searches if needed. It maintains objectivity while building a strong case through logical reasoning and legal provisions. The prosecutor responds to judicial observations with due diligence and adapts arguments to maintain prosecutorial strength.

**Legal Retriever Agent**

The Retriever agent functions as a legal research assistant with access to two vector databases. The private database stores user-specific case documents and files, while the public database contains Indian Penal Code provisions, legal statutes, and precedent case laws. The agent processes queries from the judge, lawyer, or prosecutor by formulating precise search queries and retrieving relevant legal documents. It uses ChromaDB with Ollama embeddings to perform semantic searches across the legal document corpus. The retriever evaluates result sufficiency and can indicate when additional web-based research is needed.

**Kanoon Fetcher Agent**

The Kanoon Fetcher agent specializes in retrieving similar historical cases from the Indian Kanoon database. It extracts relevant keywords from the user's case description and submitted documents using an LLM-based extraction process. The agent selects the top 5 most relevant legal terms and searches for precedent cases that match the current case's characteristics. This provides both prosecution and defense with historical context and precedent-based arguments. The fetcher operates at the beginning of the trial workflow to establish foundational research.

**Web Search Agent**

The Web Searcher agent provides additional research capabilities by searching the internet for legal information not found in local databases. It uses the Serper API to conduct targeted searches based on specific queries from the lawyer or prosecutor. The agent is invoked only when local database results are insufficient or when specific external information is required. It returns relevant search results that agents can cite in their arguments. This ensures comprehensive research coverage beyond the local legal document corpus.

**Verdict Agent**

The Verdict agent generates the final judgment after the debate concludes. It receives the complete trial transcript including all arguments, rebuttals, evidence presented, and judicial observations. The agent synthesizes this information to produce a structured verdict that includes findings of fact, application of law, legal reasoning, and final judgment. The verdict is guaranteed to be delivered through multiple safety mechanisms built into the workflow. The agent ensures the decision is legally sound and addresses all key points raised during the trial.

### Vector Database System

The system uses ChromaDB as its vector database for semantic search across legal documents. Two separate collections are maintained:

**Public Document Store**: Contains general legal reference materials including Indian Penal Code sections, legal statutes, case law precedents, and legal commentaries. This database is shared across all cases and provides the foundational legal knowledge base.

**Private Document Store**: Stores case-specific documents uploaded by users including case files, evidence documents, witness statements, and related materials. This database is isolated per case to maintain data privacy.

**Embedding Process**: Documents are processed using Ollama's nomic-embed-text model which converts legal text into high-dimensional vector representations. The RecursiveCharacterTextSplitter breaks documents into semantic chunks before embedding. These embeddings enable semantic similarity search where agents can retrieve legally relevant content based on conceptual meaning rather than keyword matching.

**Retrieval Process**: When an agent queries the vector database, the query text is embedded using the same model and compared against stored document embeddings using cosine similarity. The system returns the most semantically relevant legal passages along with their source metadata. This enables agents to access precise legal information without manually searching through thousands of pages.

### LangGraph Workflow Orchestration

The trial workflow is implemented as a state machine using LangGraph. Each agent is represented as a node, and edges define the flow of control between agents. The workflow maintains a shared state object that accumulates all messages, decisions, and context as the trial progresses.

The workflow implements conditional routing where the judge's decisions determine which agent speaks next. Smart triggers detect debate completion based on iteration count and argument patterns. Multiple safety mechanisms ensure verdict delivery: the router begins winding down at iteration 16, automatic verdict forcing occurs at iteration 18, and emergency verdict generation activates at iteration 22 if needed.

State checkpointing through MemorySaver allows the workflow to track its progress and recover from errors. The streaming architecture enables real-time updates to users as each agent contributes to the trial.

## Project Structure

```
law_courtroom_simulator/
├── agents/                    # AI agent implementations
│   ├── judge.py              # Judge orchestration and evaluation
│   ├── lawyer.py             # Defense lawyer logic
│   ├── prosecutor.py         # Prosecution logic
│   ├── retriever.py          # Vector database retrieval
│   ├── kanoon_fetcher.py     # Case law precedent fetching
│   ├── web_search.py         # Web search integration
│   ├── verdict_agent.py      # Final verdict generation
│   └── base.py               # Shared agent base classes
│
├── core/                      # Core system components
│   ├── workflow.py           # LangGraph workflow orchestration
│   ├── state.py              # Shared state management
│   ├── chroma_store.py       # ChromaDB vector store interface
│   └── config.py             # System configuration
│
├── interface/                 # User interfaces
│   └── stapp.py              # Streamlit web interface
│
├── private_documents/         # User case-specific documents
├── public_documents/          # Legal reference materials (IPC, statutes)
├── chroma_db/                # Vector database storage
│
├── app.py                    # FastAPI backend server
├── test_api_demo.py          # API testing client
├── verify_setup.py           # Installation verification
├── setup.bat                 # Automated setup script (Windows)
├── requirements.txt          # Python dependencies
├── sample_case.txt           # Example case file
└── .env                      # Environment configuration
```

## API Reference

**Endpoint:** `POST /stream_workflow`

Streams trial proceedings in real-time using Server-Sent Events.

**Request Body:**
```json
{
  "user_prompt": "Your case description and details"
}
```

**Response:** Server-Sent Events stream with JSON payloads containing agent messages, status updates, and final verdict.

**Example Usage:**
```python
import requests

url = "http://localhost:8000/stream_workflow"
data = {"user_prompt": "Your case details here"}

response = requests.post(url, json=data, stream=True)
for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```
