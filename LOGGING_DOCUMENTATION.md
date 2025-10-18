# Logging Enhancements - Complete Documentation

## Overview

Added comprehensive logging throughout the application to provide visibility into every step of the workflow execution. All emojis have been removed for cleaner, professional output.

---

## Changes Made

### 1. app.py - Application Startup & API Logging

**Added:**
- Startup initialization logging with clear sections
- LLM configuration details
- Agent initialization tracking
- API request logging with timestamps
- Event streaming counters

**Output Example:**
```
================================================================================
OLLAMA LLM INITIALIZATION
================================================================================
Ollama Base URL: http://localhost:11434
Primary Model: llama3.1:8b
Advanced Model: mistral:7b
Primary LLM initialized successfully
Fallback LLM count: 3
================================================================================

WORKFLOW INITIALIZATION
================================================================================
Creating agent instances...
  - LawyerAgent
  - ProsecutorAgent
  - JudgeAgent
  - RetrieverAgent
  - FetchingAgent (Kanoon)
  - WebSearcherAgent
All agents initialized successfully
Workflow graph compiled
================================================================================

================================================================================
NEW API REQUEST RECEIVED
================================================================================
Prompt length: 1686 characters
First 200 chars: Case File...
Starting workflow stream...
================================================================================
[API] Sending event #1 to client: progress
[API] Sending event #2 to client: progress
...
[API] Stream completed. Total events sent: 15
================================================================================
```

---

### 2. core/workflow.py - Workflow Execution Logging

**Added:**
- Workflow start timestamp
- Iteration counter with timing
- Node execution details
- State information (next node, message count)
- Time elapsed for each iteration
- User feedback checkpoint logging
- END state detection logging
- Error logging with stack traces

**Output Example:**
```
================================================================================
WORKFLOW EXECUTION STARTED
================================================================================
Initial state created
  Starting node: kanoon_fetcher
  Thought step: 0
  Message count: 1

Starting workflow stream (max 50 iterations)
--------------------------------------------------------------------------------

[ITERATION 1] Started
  Time elapsed: 0.1s
  Node: kanoon_fetcher
  Next node: prosecutor
  Messages in state: 2
  Duration: 245.3s

[ITERATION 2] Started
  Time elapsed: 245.4s
  Node: prosecutor
  Next node: judge
  Messages in state: 3
  Duration: 15.8s

[ITERATION 3] Started
  Time elapsed: 261.2s
  Node: judge
  Next node: lawyer
  Messages in state: 4
  Duration: 12.3s

[USER FEEDBACK] Checkpoint reached at iteration 7
  Providing automatic feedback: Please strengthen the arguments with more...
  Resuming workflow after feedback...

[ITERATION 8] Started (post-feedback)
  Time elapsed: 340.5s
  Node: lawyer
  Next node: judge
  Messages in state: 8
  Duration: 18.2s

[WORKFLOW END] Reached END state at iteration 15
Total time: 420.7s
```

---

### 3. agents/kanoon_fetcher.py - Kanoon API Logging

**Added:**
- Agent start banner
- File loading details
- Keyword extraction timing
- API search progress with time estimates
- Individual keyword search timing
- Document fetch counters
- Total time tracking

**Output Example:**
```
================================================================================
KANOON FETCHER AGENT - STARTED
================================================================================
User case message length: 1686 characters
Data directory: public_documents
Initializing Indian Kanoon API client...
API client initialized

Reading user documents from: private_documents
  Loaded: Case File.txt (2484 chars)
Total documents loaded: 1

--------------------------------------------------------------------------------
KEYWORD EXTRACTION - STEP 1
--------------------------------------------------------------------------------
Invoking KeywordExtractorAgent...
Keyword extraction completed in 45.2s
Keywords extracted: 9

--------------------------------------------------------------------------------
KANOON API SEARCH - STEP 2
--------------------------------------------------------------------------------
Extracted Keywords:
  [1] Defamation under Section 499 IPC
  [2] Cyber harassment under IT Act 2000
  [3] Account compromise / Hacking Defense

Search parameters:
  Max keywords to use: 3
  Max documents per keyword: 1
  Expected API calls: 3
  Estimated time: 180-360 seconds

[1/3] Searching keyword: Defamation under Section 499 IPC...
            Found 1 documents in 95.3s
[2/3] Searching keyword: Cyber harassment under IT Act 2000...
            Found 1 documents in 78.6s
[3/3] Searching keyword: Account compromise / Hacking Defense...
            Found 1 documents in 102.1s

Search completed:
  Total documents fetched: 3
  Total time: 276.0s
--------------------------------------------------------------------------------
```

---

### 4. core/chroma_store.py - Vector Store Logging

**Removed:**
- All emoji characters
- Replaced with clean text indicators

**Output Example:**
```
============================================================
Initializing ChromaVectorStore: 'private'
============================================================
Documents path: ./private_documents
Persist directory: ./chroma_db/private
Embedding model: nomic-embed-text

Initializing Ollama embeddings...  [OK]
Initializing text splitter (chunk_size=5000)...  [OK]
Initializing ChromaDB client...  [OK]
Initializing vector store collection 'private_collection'...  [OK]

[CACHE] Found existing vector store with 1 embeddings
[CACHE] Skipping re-indexing (data already cached)
   Delete './chroma_db/private' folder to force re-indexing

ChromaVectorStore 'private' initialized successfully!
============================================================
```

---

### 5. test_api_demo.py - Client Logging

**Added:**
- Connection establishment timing
- Event counter with timestamps
- Time delta between events
- Agent completion tracking
- Total execution time summary

**Removed:**
- All emoji characters

**Output Example:**
```
================================================================================
PathRAG Court Simulator - API Demo
================================================================================

Case Summary:
--------------------------------------------------------------------------------
Defendant: Rohan Malhotra (28, Entrepreneur)
Charges: Defamation (IPC 499) + Cyber Harassment (IT Act 2000)
Defense: Account hacking/compromise
--------------------------------------------------------------------------------

[CLIENT] Sending case to API...
[CLIENT] Endpoint: http://localhost:8000/stream_workflow
[CLIENT] Payload size: 1686 bytes
[CLIENT] Timeout: 1800 seconds (30 minutes)

[CLIENT] Establishing connection...
[CLIENT] Connection established in 0.45s
[CLIENT] Streaming workflow responses...
[NOTE] First agent (Kanoon Fetcher) may take 3-5 minutes (external API)

================================================================================
WORKFLOW EXECUTION:
================================================================================

[Event #1] Time: 0.5s (delta: 0.5s)
  Status: progress
  Content: Workflow initialized, starting execution...

[Event #2] Time: 245.8s (delta: 245.3s)
  Status: progress
  Agent: kanoon_fetcher
  Info: Iteration 1, Next: prosecutor

[Event #3] Time: 261.6s (delta: 15.8s)
  Status: progress
  Agent: prosecutor
  Info: Iteration 2, Next: judge

[Event #15] Time: 420.9s (delta: 18.3s)
  Status: done
  Content: Workflow completed with verdict

================================================================================
WORKFLOW COMPLETE
================================================================================

[SUMMARY]
  Total events received: 15
  Total time: 420.9s (7.0 minutes)

[CLIENT] Demo completed successfully!
```

---

## Key Improvements

### 1. Visibility
- **Every step** is logged with clear identifiers
- **Timing information** for each operation
- **State transitions** are tracked
- **Error details** with stack traces

### 2. Progress Tracking
- **Iteration counters** show workflow progress
- **Time deltas** between events
- **Estimated completion times** for long operations
- **Clear section separators** (80-char lines)

### 3. Debugging Support
- **Detailed error messages** with context
- **State information** (next node, message counts)
- **API call tracking** (Kanoon searches)
- **Cache hit/miss logging**

### 4. Professional Output
- **No emojis** - Clean, parseable text
- **Consistent formatting** - 80-char sections
- **Hierarchical structure** - Clear indentation
- **Timestamps** - Track execution time

---

## Logging Levels

### Application Level (app.py)
```
[Level: INFO] Initialization and configuration
[Level: DEBUG] API request/response details
[Level: INFO] Event streaming progress
```

### Workflow Level (workflow.py)
```
[Level: DEBUG] Iteration details
[Level: INFO] Agent transitions
[Level: WARNING] Empty states
[Level: ERROR] Exceptions with traces
```

### Agent Level (kanoon_fetcher.py)
```
[Level: INFO] Agent start/end
[Level: DEBUG] File loading
[Level: INFO] API search progress
[Level: DEBUG] Individual keyword timing
```

### Client Level (test_api_demo.py)
```
[Level: INFO] Connection status
[Level: DEBUG] Event details
[Level: INFO] Completion summary
```

---

## Interpreting the Logs

### Normal Execution Pattern

1. **Startup** (5-10s):
   ```
   OLLAMA LLM INITIALIZATION
   WORKFLOW INITIALIZATION
   ```

2. **Kanoon Fetcher** (3-5 minutes):
   ```
   [ITERATION 1] kanoon_fetcher
   KANOON FETCHER AGENT - STARTED
   KEYWORD EXTRACTION - STEP 1 (45s)
   KANOON API SEARCH - STEP 2 (180-360s)
   ```

3. **Main Workflow** (2-3 minutes):
   ```
   [ITERATION 2] prosecutor
   [ITERATION 3] judge
   [ITERATION 4] lawyer
   [ITERATION 5] retriever
   [ITERATION 6] judge
   [ITERATION 7] lawyer
   [USER FEEDBACK] checkpoint
   ...continues...
   ```

4. **Completion**:
   ```
   [WORKFLOW END] Reached END state
   Total time: 420.7s
   ```

### Signs of Issues

**Stuck in Loop:**
```
[ITERATION 50] ...
[MAX ITERATIONS] Reached limit of 50
```

**API Errors:**
```
[1/3] Searching keyword: ...
            Error: Connection timeout
```

**Empty States:**
```
WARNING: Received empty state, skipping...
```

**Exceptions:**
```
[ERROR] Workflow stream exception
  Error type: ConnectionResetError
  Error message: ...
[Stack trace follows]
```

---

## Performance Monitoring

### Time Benchmarks

**Expected Times:**
- **Startup**: 5-10s (with cache)
- **Kanoon Fetcher**: 180-360s (3-6 minutes)
- **Per Agent**: 10-30s
- **Total Workflow**: 420-600s (7-10 minutes)

**Warning Signs:**
- Agent taking > 60s (except Kanoon)
- Time delta > 120s between events
- Total time > 900s (15 minutes)

### Monitoring Commands

**Watch logs in real-time:**
```bash
# Terminal 1 - Server logs
python app.py | tee server.log

# Terminal 2 - Client logs
python test_api_demo.py | tee client.log
```

**Check for specific patterns:**
```bash
# Find all iteration timings
grep "ITERATION" server.log

# Find errors
grep "ERROR\|Exception" server.log

# Find agent completions
grep "Agent.*completed" server.log
```

---

## Troubleshooting with Logs

### Problem: Workflow seems stuck

**Check:**
1. Last iteration number
2. Time since last event
3. Current agent

**Example:**
```
[ITERATION 8] Started
  Time elapsed: 456.2s
  Node: kanoon_fetcher
  [No output for 5+ minutes]
```
**Diagnosis:** Kanoon API slow/hung

---

### Problem: High iteration count

**Check:**
```
[ITERATION 45] ...
[ITERATION 46] ...
```
**Diagnosis:** Feedback loop not terminating

---

### Problem: Connection lost

**Check:**
```
[API] Sending event #5 to client: progress
[No more API logs]

[CLIENT] Connection established...
[Event #1] ...
[Event #5] ...
[ERROR] Could not connect to API server
```
**Diagnosis:** Server crashed, check server.log for exceptions

---

## Files Modified

1. **app.py** - Added initialization and API logging
2. **core/workflow.py** - Added iteration and timing logs
3. **agents/kanoon_fetcher.py** - Added agent execution logs
4. **core/chroma_store.py** - Removed emojis
5. **test_api_demo.py** - Added client-side logging

---

## Benefits

1. **Complete Visibility** - Know exactly what's happening
2. **Performance Monitoring** - Track execution times
3. **Easy Debugging** - Detailed error information
4. **Professional Output** - Clean, parseable logs
5. **No Guessing** - Clear progress indicators

---

**Last Updated:** 2025-10-18  
**Status:** Production Ready  
**Log Format:** Text-based, no emojis, 80-char sections
