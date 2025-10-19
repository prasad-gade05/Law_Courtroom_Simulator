# Law Courtroom Simulator 🏛️⚖️

An AI-powered legal case simulation platform that recreates authentic courtroom proceedings using multi-agent orchestration, RAG (Retrieval-Augmented Generation), and **Google Gemini 2.5 Flash Lite** for fast, cloud-based inference.

## 🎯 What Is This?

Law Courtroom Simulator is a virtual courtroom where AI agents simulate a real legal trial. Think of it as a video game for lawyers where you can:

- **Practice legal cases** without real-world consequences
- **Test arguments** before going to actual court
- **Learn from AI judges, lawyers, and prosecutors**
- **Get instant legal research** from Indian laws and precedents
- **Experiment with different defense strategies**

### Key Features

✅ **6 AI Agents** - Judge, Defense Lawyer, Prosecutor, Legal Researcher, Case Finder, Web Searcher  
✅ **Cloud-Powered** - Google Gemini 2.5 Flash Lite (fastest model)  
✅ **No GPU Needed** - Runs entirely in the cloud  
✅ **Under 5 Minutes** - Complete legal simulations fast  
✅ **Smart Research** - Automatically finds relevant laws and cases  
✅ **Two Interfaces** - Web UI (Streamlit) + REST API

## 📋 Table of Contents

1. [How It Works (Simple Explanation)](#-how-it-works-simple-explanation)
2. [Quick Start (Setup in 10 Minutes)](#-quick-start-setup-in-10-minutes)
3. [Running the Application](#-running-the-application)
4. [Using Your Own Cases](#-using-your-own-cases)
5. [Understanding the Agents](#-understanding-the-agents)
6. [Configuration Options](#-configuration-options)
7. [Troubleshooting](#-troubleshooting)
8. [Project Structure](#-project-structure)
9. [API Reference](#-api-reference)
10. [Cost & Performance](#-cost--performance)

---

## 🧠 How It Works (Simple Explanation)

Imagine a courtroom with 6 AI people working together:

### The 6 AI Agents (Characters):

1. **👨‍⚖️ Judge** - Controls everything, decides who speaks, gives final verdict
2. **🛡️ Defense Lawyer** - Defends you, builds arguments in your favor
3. **⚔️ Prosecutor** - Argues against you, finds evidence of wrongdoing
4. **📚 Legal Retriever** - Searches Indian Penal Code (IPC) for relevant laws
5. **🔍 Kanoon Fetcher** - Finds similar past court cases from Indian Kanoon
6. **🌐 Web Searcher** - Searches internet for additional legal info

### What Happens When You Run It:

```
You submit a case → Kanoon Fetcher finds similar cases → 
Prosecutor builds case against you → Judge reviews → 
Legal Retriever finds relevant laws → Defense Lawyer argues for you → 
You give feedback → Cycle repeats 5-10 times → 
Judge gives final verdict
```

### The Technology Stack:

- **Google Gemini 2.5 Flash Lite** - The AI "brain" (runs in cloud, no GPU needed)
- **ChromaDB** - Smart filing system for legal documents
- **FastAPI** - Communication system (REST API)
- **Streamlit** - Visual web interface
- **LangGraph** - Orchestrates the agent workflow

---

## 🚀 Quick Start (Setup in 10 Minutes)

### Step 1: Prerequisites ✅

Before starting, make sure you have:

- **Windows 10/11** (tested on Windows 11)
- **Python 3.9 or higher** - [Download here](https://www.python.org/downloads/)
- **Internet connection** (required for cloud API)
- **8+ GB RAM** (16 GB recommended)
- **5 GB free disk space**

### Step 2: Get Google AI API Key (Free) 🔑

1. Visit **[Google AI Studio](https://aistudio.google.com/app/apikey)**
2. Sign in with your Google account
3. Click **"Create API Key"** or **"Get API Key"**
4. Copy the key (looks like: `AIzaSyB1234...`)
5. **Save it** - you'll need it in Step 5

**Free Tier Limits:**
- 15 requests per minute
- 1 million tokens per day
- Perfect for personal use and testing

### Step 3: Download the Project 📥

```bash
# Clone the repository
git clone https://github.com/prasad-gade05/Law_Courtroom_Simulator
cd Law_Courtroom_Simulator
```

Or download as ZIP and extract.

### Step 4: Automated Installation 🔧

Run the setup script (does everything automatically):

```bash
setup.bat
```

**What this does:**
- ✅ Checks if Python is installed
- ✅ Creates a virtual environment (`venv` folder)
- ✅ Installs all required packages (FastAPI, LangChain, Google AI, etc.)
- ✅ Creates necessary folders (`private_documents`, `chroma_db`)
- ✅ Sets up configuration files

**Wait for:** "Setup complete!" message (takes 3-5 minutes)

### Step 5: Configure Your API Key 🔐

Create your environment file:

```bash
# Copy the example file
copy .env.example .env
```

Open `.env` in Notepad and add your API key:

```env
# Required: Your Google API Key
GOOGLE_API_KEY=AIzaSyB1234...your_actual_key_here

# Model Configuration (using fastest model)
GEMINI_MODEL=gemini-2.5-flash-lite
GEMINI_EMBEDDING_MODEL=text-embedding-004

# Optional APIs (can leave empty)
SERPER_API_KEY=
KANOON_API_KEY=
```

**Important:** Replace `AIzaSyB1234...` with your actual API key from Step 2.

### Step 6: Verify Everything Works ✔️

```bash
# Activate the virtual environment
venv\Scripts\activate

# Run verification
python verify_setup.py
```

**Expected output:**
```
✓ Python version: 3.11.x
✓ Virtual environment: Active
✓ Dependencies: Installed
✓ Google API Key: Valid
✓ Gemini Model: Accessible
✓ Directories: Created
✓ All checks passed!
```

If you see errors, check [Troubleshooting](#-troubleshooting).

---

## 🎮 Running the Application

You have 2 ways to use the simulator:

### Method 1: Quick Test (Command Line) - Fastest Way

**Perfect for:** Testing, automation, quick checks

#### Start the Backend Server:

```bash
# Activate environment (if not already active)
venv\Scripts\activate

# Start the FastAPI server
python app.py
```

**Wait for this message:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
All agents initialized successfully
Workflow graph compiled
```

#### Run a Test Case:

Open a **new terminal** and run:

```bash
# Test with the included sample case
python test_api_demo.py
```

Or test with your own case file:

```bash
python test_api_demo.py your_case_file.txt
```

**What you'll see:**
- Real-time streaming updates
- Agent responses (Judge, Lawyer, Prosecutor)
- Legal research findings
- Final verdict
- Complete in 3-5 minutes

### Method 2: Web Interface (Interactive) - Best User Experience

**Perfect for:** Visual interaction, presentations, learning

#### Step 1 - Start Backend (Terminal 1):

```bash
venv\Scripts\activate
python app.py
```

#### Step 2 - Start Web UI (Terminal 2):

```bash
venv\Scripts\activate
streamlit run interface/stapp.py
```

**Browser opens automatically** to `http://localhost:8501`

#### Step 3 - Use the Interface:

1. **Upload Documents** (Optional)
   - Click "Upload Case Documents"
   - Add PDFs, Word docs, or text files
   - These get added to the knowledge base

2. **Enter Your Case**
   - Describe your legal case in the text box
   - Or paste case details

3. **Start Simulation**
   - Click "Start Court Simulation"
   - Watch agents work in real-time

4. **Provide Feedback**
   - When prompted, you can add feedback
   - Strengthens defense arguments

5. **Review Verdict**
   - Read the final judgment
   - See legal reasoning
   - Download report (optional)

---

## 📝 Using Your Own Cases

### Sample Case Included

The project includes `sample_case.txt` - a defamation and cyber harassment case:

**Case:** State vs. Rohan Malhotra  
**Charges:** Defamation (IPC 499) + IT Act violations  
**Scenario:** Accused claims social media account was hacked

**To run it:**
```bash
python test_api_demo.py sample_case.txt
```

### Creating Your Own Case File

Create a text file (e.g., `my_case.txt`) following this template:

```text
Case File

Case Title: [Your Case Name - e.g., "State vs. John Doe"]

Case Summary:
[Detailed description of what happened. Include:
- Who is involved (accused, victim, witnesses)
- What allegedly happened (the incident)
- When it happened (dates)
- Where it happened (location)
- Why it's a legal issue (laws violated)]

Case Details:
1. Date of Incident: [e.g., January 15, 2024]
2. Location: [e.g., Mumbai, Maharashtra]
3. Nature of Offense: [e.g., Theft under IPC Section 378]
4. Evidence Available: [e.g., CCTV footage, witness statements]
5. Parties Involved:
   - Accused: [Name, age, occupation]
   - Victim: [Name, age, occupation]

Defense Position:
1. [Main defense argument - e.g., "Accused has alibi"]
2. [Supporting point - e.g., "Witness testimony confirms location"]
3. [Additional defense - e.g., "No motive for the crime"]
4. [Evidence for defense - e.g., "Phone records show different location"]

Prosecution Claims:
1. [Main prosecution argument]
2. [Evidence against accused]
3. [Witness statements]

Request:
[What you want analyzed - e.g., "Provide defense strategy for this 
theft case under IPC Section 378, considering the alibi defense"]
```

### Tips for Better Results:

✅ **Be Specific** - More details = better analysis  
✅ **Include Evidence** - Mention what proof exists  
✅ **Cite Laws** - If you know relevant IPC sections, mention them  
✅ **Clear Timeline** - Dates and sequence of events help  
✅ **Both Sides** - Include prosecution and defense viewpoints

### Adding Supporting Documents:

1. Place documents in `private_documents/` folder:
   - PDFs (case files, evidence photos)
   - Word documents (witness statements)
   - Text files (legal research)

2. The system automatically processes them when you run

### Example Case Types You Can Test:

- **Criminal Cases** - Theft, assault, defamation, fraud
- **Cyber Crimes** - Hacking, online harassment, identity theft
- **Property Disputes** - Land disputes, trespassing
- **Contract Issues** - Breach of contract, fraud
- **Family Law** - Custody, domestic violence

---

## 🤖 Understanding the Agents

### 1. Judge Agent 👨‍⚖️

**Role:** Master of Ceremonies, Decision Maker

**What it does:**
- Controls the entire trial flow
- Decides which agent speaks next
- Requests evidence verification
- Ensures fair proceedings
- Delivers final verdict with legal reasoning

**When it acts:**
- After prosecutor presents case
- When verifying legal claims
- Before final verdict
- To request additional research

### 2. Defense Lawyer Agent 🛡️

**Role:** Your Advocate, Defender

**What it does:**
- Builds arguments in your favor
- Finds weaknesses in prosecution's case
- Cites relevant laws and precedents
- Prepares cross-examination questions
- Proposes defenses (alibi, self-defense, etc.)

**When it acts:**
- After prosecution's arguments
- When user provides feedback
- To present counterarguments
- During final arguments

### 3. Prosecutor Agent ⚔️

**Role:** State's Representative, Accuser

**What it does:**
- Builds the case against the accused
- Finds evidence of wrongdoing
- Cites laws that were violated
- Challenges defense arguments
- Presents aggravating factors

**When it acts:**
- Early in the workflow (sets the stage)
- After legal research is done
- To rebut defense arguments
- During closing arguments

### 4. Legal Retriever Agent 📚

**Role:** Law Library, Legal Researcher

**What it does:**
- Searches Indian Penal Code (IPC) documents
- Finds relevant sections and laws
- Retrieves legal definitions
- Provides legal precedents from database
- Uses RAG (Retrieval-Augmented Generation)

**What it searches:**
- Public documents in `public_documents/`
- IPC sections, legal provisions
- Constitutional articles
- Your uploaded documents in `private_documents/`

**When it acts:**
- When judge requests verification
- When lawyers need legal backing
- To clarify legal definitions

### 5. Kanoon Fetcher Agent 🔍

**Role:** Case Law Researcher, Precedent Finder

**What it does:**
- Searches Indian Kanoon database
- Finds similar past court cases
- Extracts relevant keywords from your case
- Retrieves judgments and precedents
- Provides citation for legal arguments

**When it acts:**
- At the beginning (analyzes your case)
- To find supporting precedents
- When similar case law needed

**Note:** Requires KANOON_API_KEY (optional)

### 6. Web Searcher Agent 🌐

**Role:** Internet Researcher, Current Info Finder

**What it does:**
- Searches the internet for legal information
- Finds recent judgments not in database
- Looks up legal experts' opinions
- Searches for case updates
- Provides current legal trends

**When it acts:**
- When local database lacks info
- For recent legal developments
- To verify facts
- When asked by other agents

**Note:** Requires SERPER_API_KEY (optional)

### How They Work Together:

```
1. User submits case
2. Kanoon Fetcher extracts keywords, finds similar cases
3. Prosecutor builds charges
4. Judge reviews, requests Legal Retriever for laws
5. Legal Retriever fetches IPC sections
6. Defense Lawyer builds counter-arguments
7. User provides feedback (optional)
8. [Cycle repeats 5-10 times with different angles]
9. Judge delivers final verdict
```

---

## ⚙️ Configuration Options

### Environment Variables (.env file)

```env
# ============================================
# REQUIRED CONFIGURATION
# ============================================

# Your Google AI API Key (REQUIRED)
GOOGLE_API_KEY=your_google_api_key_here

# ============================================
# MODEL CONFIGURATION
# ============================================

# Gemini Model (Choose based on needs)
GEMINI_MODEL=gemini-2.5-flash-lite

# Available models:
# - gemini-2.5-flash-lite  (Fastest, cheapest, recommended)
# - gemini-1.5-flash       (Fast, good quality)
# - gemini-1.5-pro         (Best quality, slower, costlier)
# - gemini-2.0-flash-exp   (Experimental, very fast)

# Embedding Model (for document search)
GEMINI_EMBEDDING_MODEL=text-embedding-004

# ============================================
# OPTIONAL EXTERNAL APIS
# ============================================

# Serper API for web search (optional)
# Get free key: https://serper.dev/
SERPER_API_KEY=

# Indian Kanoon API for case law (optional)
KANOON_API_KEY=

# ============================================
# PERFORMANCE TUNING (Advanced)
# ============================================

# Temperature (creativity vs accuracy)
# Lower = more focused, Higher = more creative
# Default: 0.7 (balanced)
TEMPERATURE=0.7

# Max tokens per response
# Default: 2048
MAX_TOKENS=2048
```

### Choosing the Right Model:

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| gemini-2.5-flash-lite | ⚡⚡⚡ Fastest | ⭐⭐⭐ Good | 💰 Cheapest | Testing, demos |
| gemini-1.5-flash | ⚡⚡ Fast | ⭐⭐⭐⭐ Better | 💰💰 Low | Production use |
| gemini-1.5-pro | ⚡ Slower | ⭐⭐⭐⭐⭐ Best | 💰💰💰 Higher | Complex cases |
| gemini-2.0-flash-exp | ⚡⚡⚡ Very Fast | ⭐⭐⭐⭐ Excellent | 💰 Low | Experimental |

**Recommendation:** Start with `gemini-2.5-flash-lite` for best speed/cost ratio.

### Switching Models:

1. Open `.env` file
2. Change `GEMINI_MODEL=gemini-2.5-flash-lite` to your choice
3. Save file
4. Restart `python app.py`

No code changes needed!

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### ❌ Error: "GOOGLE_API_KEY not found"

**Problem:** The .env file is missing or API key not set

**Solution:**
```bash
# Create .env file from template
copy .env.example .env

# Open in Notepad and add your key
notepad .env

# Add this line:
GOOGLE_API_KEY=your_actual_api_key_here
```

#### ❌ Error: "Invalid API key" or "API key not valid"

**Problem:** Wrong or expired API key

**Solution:**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Check if key is active
3. Create new key if needed
4. Copy ENTIRE key (no spaces)
5. Update .env file
6. Restart app

#### ❌ Error: "Rate limit exceeded"

**Problem:** Too many requests (free tier limit: 15/minute)

**Solution:**
- Wait 60 seconds and try again
- Reduce workflow complexity
- Upgrade to paid tier for higher limits
- Check if multiple instances are running

#### ❌ Error: "ModuleNotFoundError: No module named 'langchain'"

**Problem:** Dependencies not installed

**Solution:**
```bash
# Make sure virtual environment is active
venv\Scripts\activate

# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall

# Verify
python verify_setup.py
```

#### ❌ Error: "Port 8000 already in use"

**Problem:** Another process using port 8000

**Solution:**
```bash
# Find the process
netstat -ano | findstr :8000

# Kill it (use PID from above)
taskkill /F /PID <process_id>

# Or use different port
uvicorn app:app --host 0.0.0.0 --port 8001
```

#### ❌ ChromaDB is very slow on first run

**Problem:** Generating embeddings for all documents

**Solution:**
- This is normal on FIRST run only
- Wait for progress to complete (can take 5-10 minutes)
- Subsequent runs use cached embeddings (instant)
- Watch console for progress messages

#### ❌ Error: "Internet connection required"

**Problem:** No internet access

**Solution:**
- Gemini is cloud-based, REQUIRES internet
- Check your connection
- Check firewall/proxy settings
- Try with VPN if blocked

#### ❌ Agents giving poor quality responses

**Problem:** Wrong model or settings

**Solution:**
1. Switch to better model:
   ```env
   GEMINI_MODEL=gemini-1.5-flash
   ```
2. Provide more detailed case description
3. Add supporting documents to `private_documents/`
4. Try running case again

#### ❌ Error: "Python was not found"

**Problem:** Python not installed or not in PATH

**Solution:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, CHECK "Add Python to PATH"
3. Restart terminal
4. Verify: `python --version`

### Getting More Help:

**1. Run Diagnostics:**
```bash
python verify_setup.py
```

**2. Check Logs:**
- Look at terminal output for detailed errors
- Check FastAPI logs in the terminal running `app.py`

**3. Common Log Messages:**

✅ **Good signs:**
```
INFO: Uvicorn running on http://0.0.0.0:8000
Primary LLM initialized successfully
All agents initialized successfully
Workflow graph compiled
```

❌ **Problem signs:**
```
ERROR: Failed to initialize Gemini LLM
WARNING: Low VRAM
CRITICAL: API key missing
```

---

## 📁 Project Structure

```
Law_Courtroom_Simulator/
│
├── 📄 app.py                      # Main FastAPI backend server
├── 📄 requirements.txt            # Python dependencies list
├── 📄 setup.bat                   # Automated setup script (Windows)
├── 📄 verify_setup.py            # Verification tool
├── 📄 test_api_demo.py           # API testing script
├── 📄 sample_case.txt            # Example legal case
├── 📄 .env.example               # Environment template
├── 📄 .env                       # Your config (YOU create this)
├── 📄 README.md                  # This file
│
├── 📁 venv/                      # Virtual environment (created by setup.bat)
│   └── ... (Python packages)
│
├── 📁 core/                      # Core system components
│   ├── chroma_store.py          # Vector database (ChromaDB + Gemini embeddings)
│   ├── workflow.py              # LangGraph workflow orchestration
│   └── state.py                 # Agent state management
│
├── 📁 agents/                    # AI agent implementations
│   ├── __init__.py              # Agent exports
│   ├── base.py                  # Base agent class
│   ├── judge.py                 # Judge agent
│   ├── lawyer.py                # Defense lawyer agent
│   ├── prosecutor.py            # Prosecutor agent
│   ├── retriever.py             # Legal document retriever
│   ├── kanoon_fetcher.py        # Indian Kanoon integration
│   └── web_search.py            # Web search agent
│
├── 📁 interface/                 # User interfaces
│   └── stapp.py                 # Streamlit web UI
│
├── 📁 private_documents/         # Your case files (gitignored)
│   └── [Your PDFs, docs, etc.]
│
├── 📁 public_documents/          # Legal reference documents
│   └── [IPC sections, laws, precedents]
│
├── 📁 chroma_db/                # Vector database storage (gitignored)
│   └── [Embeddings cache]
│
└── 📁 _archive/                 # Old documentation (you can ignore)
    └── [Previous docs]
```

### Key Files Explained:

**You interact with:**
- `app.py` - Start this to run the backend
- `test_api_demo.py` - Run this to test cases
- `.env` - Your configuration (API keys)
- `sample_case.txt` - Example to learn from
- `private_documents/` - Put your documents here

**System uses:**
- `core/` - The brain (workflow, state, storage)
- `agents/` - The actors (judge, lawyer, etc.)
- `chroma_db/` - The memory (cached documents)

**Setup uses:**
- `setup.bat` - Installs everything
- `verify_setup.py` - Checks if working
- `requirements.txt` - List of packages needed

---

## 🔌 API Reference

### FastAPI Endpoint

**Base URL:** `http://localhost:8000`

#### POST `/stream_workflow`

Streams the trial workflow in real-time.

**Request:**
```json
{
  "user_prompt": "Your case description here..."
}
```

**Response:** Server-Sent Events (SSE) stream

**Event Format:**
```json
{
  "status": "agent_name",
  "message": "Agent response...",
  "next_agent": "next_agent_name",
  "iteration": 1,
  "completed": false
}
```

**Example (Python):**
```python
import requests

url = "http://localhost:8000/stream_workflow"
data = {"user_prompt": "Your case here"}

response = requests.post(url, json=data, stream=True)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/stream_workflow \
  -H "Content-Type: application/json" \
  -d '{"user_prompt":"Your case"}'
```

### Using test_api_demo.py

**Simplest way:**
```bash
python test_api_demo.py
```

**With custom file:**
```python
# test_api_demo.py usage
python test_api_demo.py my_case.txt
```

**What it does:**
- Reads case from file
- Sends to API
- Streams responses in real-time
- Displays formatted output
- Shows final verdict

---

## 💰 Cost & Performance

### Google Gemini 2.5 Flash Lite Pricing

**Current Rates (Check [Google AI Pricing](https://ai.google.dev/pricing)):**

- **Input tokens:** ~$0.04 per 1M tokens
- **Output tokens:** ~$0.15 per 1M tokens

**Typical Usage:**

| Scenario | Tokens Used | Estimated Cost |
|----------|-------------|----------------|
| Single simple case | ~30K tokens | ~$0.01 |
| Single complex case | ~80K tokens | ~$0.02 |
| 10 cases per day | ~500K tokens | ~$0.10 |
| 100 cases per month | ~3M tokens | ~$0.60 |

### Free Tier Limits:

✅ **15 requests per minute**  
✅ **1 million tokens per day**  
✅ **Free forever** for personal/educational use

**Perfect for:**
- Learning and experimentation
- Personal legal research
- Student projects
- Prototyping
- Small-scale use (< 50 cases/day)

### Performance Benchmarks:

**With Gemini 2.5 Flash Lite:**

| Metric | Time |
|--------|------|
| First run (with embedding) | 5-8 minutes |
| Document indexing | 1-3 minutes (once) |
| Workflow execution | 2-4 minutes |
| Subsequent runs | 2-3 minutes |
| Single agent response | 5-15 seconds |

**System Requirements:**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 10 | Windows 11 |
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16 GB |
| Storage | 5 GB free | 10 GB+ free |
| Internet | Required | Broadband |
| GPU | NOT needed | NOT needed |

### Comparison with Local Models:

| Metric | Local (Ollama) | Cloud (Gemini) |
|--------|----------------|----------------|
| Setup Time | 30+ minutes | 5 minutes |
| Workflow Time | 40+ minutes | 2-4 minutes |
| GPU Required | Yes (6GB+ VRAM) | No |
| Cost | Free | ~$0.01/case |
| Consistency | Variable | Reliable |
| Internet | Optional | Required |

---

## 🔒 Privacy & Security

### Data Handling:

⚠️ **Important:** Your data is sent to Google Cloud for processing

**What Google receives:**
- Your case descriptions
- Legal queries
- Document contents (when uploaded)

**Google's promises:**
- Data encrypted in transit (HTTPS)
- Not used to train public models
- Not shared with third parties
- Processed and discarded per API terms

**Read:** [Google AI Privacy Policy](https://ai.google.dev/gemini-api/terms)

### Your Data Locally:

✅ **ChromaDB** - Embeddings stored encrypted on your machine  
✅ **Documents** - Stay in `private_documents/` (not uploaded unless queried)  
✅ **Logs** - Only stored locally

### Best Practices:

- ✅ Use test data for learning
- ✅ Anonymize real cases before testing
- ⚠️ Don't submit confidential attorney-client information
- ✅ Clear `chroma_db/` periodically to remove cached data

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes
4. Test thoroughly
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **Google Gemini API** - Fast, reliable AI inference
- **LangChain** - Excellent LLM framework
- **LangGraph** - Powerful workflow orchestration
- **ChromaDB** - Efficient vector storage
- **FastAPI** - Modern API framework
- **Streamlit** - Beautiful web UI
- Legal community for domain expertise

---

## 📞 Support & Help

### Need Help?

1. **Read this README** thoroughly
2. **Run diagnostics:** `python verify_setup.py`
3. **Check troubleshooting** section above
4. **Review logs** in terminal
5. **Open GitHub issue** with:
   - Error message
   - Steps to reproduce
   - Output of `verify_setup.py`

### Quick Links:

- 🌐 [Google AI Studio](https://aistudio.google.com/)
- 📖 [Gemini API Docs](https://ai.google.dev/docs)
- 💰 [Pricing](https://ai.google.dev/pricing)
- 🔐 [Privacy Policy](https://ai.google.dev/gemini-api/terms)

---

## 🎉 Ready to Start?

```bash
# 1. Activate environment
venv\Scripts\activate

# 2. Start backend
python app.py

# 3. Test it (new terminal)
python test_api_demo.py
```

**Expected:** Fast responses, professional legal analysis, verdict in 2-4 minutes! ⚖️

---

**Made with ❤️ for legal professionals, students, and AI enthusiasts**


