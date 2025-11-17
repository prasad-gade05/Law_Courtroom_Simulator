# Lex Simulacra - System Diagrams and Visualizations

This document contains all the text-based diagrams and visualizations for the Lex Simulacra project.

---

## Figure 1: System Architecture Diagram

```
                          ┌─────────────────────┐
                          │       USER          │
                          └──────────┬──────────┘
                                     │
                                     ↓
              ┌──────────────────────────────────────────┐
              │     PRESENTATION LAYER                    │
              │  ┌────────────────────────────────────┐  │
              │  │   Streamlit Web Interface          │  │
              │  │  - Real-time Updates               │  │
              │  │  - Color-coded Agent Cards         │  │
              │  │  - Timeline Tracking               │  │
              │  │  - Metrics Display                 │  │
              │  └────────────────────────────────────┘  │
              └──────────────────┬───────────────────────┘
                                 │ HTTP/SSE
                                 ↓
              ┌──────────────────────────────────────────┐
              │     APPLICATION LAYER                     │
              │  ┌────────────────────────────────────┐  │
              │  │   FastAPI Backend                  │  │
              │  │  - /stream_workflow endpoint       │  │
              │  │  - Server-Sent Events (SSE)        │  │
              │  │  - Async Event Generator           │  │
              │  └────────────────────────────────────┘  │
              └──────────────────┬───────────────────────┘
                                 │
                                 ↓
              ┌──────────────────────────────────────────┐
              │   WORKFLOW ORCHESTRATION LAYER            │
              │  ┌────────────────────────────────────┐  │
              │  │   LangGraph StateGraph             │  │
              │  │  - State Management                │  │
              │  │  - Conditional Routing             │  │
              │  │  - Iteration Control               │  │
              │  │  - Memory Checkpointer             │  │
              │  └────────────────────────────────────┘  │
              └──────────────────┬───────────────────────┘
                                 │
                                 ↓
    ┌────────────────────────────────────────────────────────────┐
    │                    AGENT LAYER                              │
    │                                                              │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
    │  │   Kanoon     │  │  Document    │  │   Initial    │     │
    │  │   Fetcher    │  │ Summarizer   │  │  Retriever   │     │
    │  │   Agent      │  │    Agent     │  │    Agent     │     │
    │  └──────────────┘  └──────────────┘  └──────────────┘     │
    │                                                              │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
    │  │   Defense    │  │ Prosecutor   │  │    Judge     │     │
    │  │   Lawyer     │  │    Agent     │  │    Agent     │     │
    │  │   Agent      │  │              │  │              │     │
    │  └──────────────┘  └──────────────┘  └──────────────┘     │
    │                                                              │
    │  ┌──────────────┐  ┌──────────────┐                        │
    │  │   Verdict    │  │  Web Search  │                        │
    │  │    Agent     │  │    Agent     │                        │
    │  └──────────────┘  └──────────────┘                        │
    └──────────────────────────┬─────────────────────────────────┘
                               │
                               ↓
              ┌────────────────────────────────────────┐
              │      ENHANCED RAG SYSTEM               │
              │  ┌──────────────────────────────────┐ │
              │  │  - Intelligent Chunking          │ │
              │  │  - Citation Enforcement          │ │
              │  │  - Hallucination Detection       │ │
              │  │  - Legal Re-Ranking              │ │
              │  │  - Structured Presentation       │ │
              │  │  - Context Compression           │ │
              │  └──────────────────────────────────┘ │
              └───────┬──────────────────┬─────────────┘
                      │                  │
         ┌────────────┴────────┐    ┌────┴──────────┐
         ↓                     ↓    ↓               ↓
    ┌─────────┐          ┌─────────────┐     ┌──────────┐
    │ChromaDB │          │  Kanoon API │     │  Serper  │
    │ Vector  │          │   (Indian   │     │   API    │
    │  Store  │          │  Case Law)  │     │ (Web     │
    │         │          │             │     │ Search)  │
    └─────────┘          └─────────────┘     └──────────┘
      (DATA LAYER)         (EXTERNAL APIS)
```

---

## Figure 2: Agent Interaction Sequence Diagram

```
User    Kanoon   DocSum   Retriever   Lawyer   Prosecutor   Judge   Verdict
 │         │        │          │         │          │         │        │
 │─Case───>│        │          │         │          │         │        │
 │         │        │          │         │          │         │        │
 │         │[Fetch] │          │         │          │         │        │
 │         │  Cases │          │         │          │         │        │
 │         │────────>│          │         │          │         │        │
 │         │        │          │         │          │         │        │
 │         │        │[Summarize│         │          │         │        │
 │         │        │Documents]│         │          │         │        │
 │         │        │──────────>│         │          │         │        │
 │         │        │          │         │          │         │        │
 │         │        │          │[Retrieve│          │         │        │
 │         │        │          │ Context]│          │         │        │
 │         │        │          │         │          │         │        │
 │         │        │          │         │<─Context─│         │        │
 │         │        │          │         │          │         │        │
 │         │        │          │         │┌─────────┐         │        │
 │         │        │          │         ││ Review  │         │        │
 │         │        │          │         ││ Context │         │        │
 │         │        │          │         │└─────────┘         │        │
 │         │        │          │         │          │         │        │
 │         │        │          │         │┌─────────┐         │        │
 │         │        │          │         ││Construct│         │        │
 │         │        │          │         ││Argument │         │        │
 │         │        │          │         │└─────────┘         │        │
 │         │        │          │         │          │         │        │
 │         │        │          │         │──Opening──────────>│        │
 │         │        │          │         │ Statement          │        │
 │         │        │          │         │          │         │        │
 │         │        │          │         │          │         │┌───────┐
 │         │        │          │         │          │         ││Evaluate│
 │         │        │          │         │          │         ││Arguments│
 │         │        │          │         │          │         │└───────┘
 │         │        │          │         │          │         │        │
 │         │        │          │         │          │<────────│        │
 │         │        │          │         │          │  Route  │        │
 │         │        │          │         │          │         │        │
 │         │        │          │         │          │┌────────┐        │
 │         │        │          │         │          ││Review &│        │
 │         │        │          │         │          ││Counter │        │
 │         │        │          │         │          │└────────┘        │
 │         │        │          │         │          │         │        │
 │         │        │          │         │          │─Response────────>│
 │         │        │          │         │          │         │        │
 │         │        │          │         │<─────────│─────────│        │
 │         │        │          │         │   Route to Lawyer  │        │
 │         │        │          │         │          │         │        │
 │         │        │          │         │┌─────────┐         │        │
 │         │        │          │         ││ Rebuttal│         │        │
 │         │        │          │         │└─────────┘         │        │
 │         │        │          │         │          │         │        │
 │         │        │          │         │──Rebuttal─────────>│        │
 │         │        │          │         │          │         │        │
 │         │        │          │         │          │         │        │
 │         │  [Multiple iterations: 15-20 rounds]    │        │        │
 │         │        │          │         │          │         │        │
 │         │        │          │         │          │         │──Route─>│
 │         │        │          │         │          │         │ Verdict│
 │         │        │          │         │          │         │        │
 │         │        │          │         │          │         │        │┌────────┐
 │         │        │          │         │          │         │        ││Analyze │
 │         │        │          │         │          │         │        ││Transcript│
 │         │        │          │         │          │         │        │└────────┘
 │         │        │          │         │          │         │        │
 │<─────────────────────────────────────────────────────────────Verdict│
 │         │        │          │         │          │         │        │
```

---

## Figure 3: Module Block Diagram with Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE MODULE                           │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              Streamlit (enhanced_stapp.py)                     │ │
│  │  • Case Input Form        • File Upload                        │ │
│  │  • Agent Cards Display    • Timeline Visualization             │ │
│  │  • Metrics Dashboard      • Real-time Streaming                │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │ HTTP POST /stream_workflow
                                   │ user_prompt data
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         API MODULE                                   │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    FastAPI (app.py)                            │ │
│  │  • POST /stream_workflow endpoint                              │ │
│  │  • Server-Sent Events (SSE) streaming                          │ │
│  │  • Async event generator                                       │ │
│  │  • JSON response formatting                                    │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │ invoke workflow.run()
                                   │ with user_prompt
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│                WORKFLOW ORCHESTRATION MODULE                         │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │            LangGraph StateGraph (workflow.py)                  │ │
│  │  • StateGraph with AgentState                                  │ │
│  │  • Node definitions for 8 agents                               │ │
│  │  • Conditional edge routing                                    │ │
│  │  • Iteration tracking (limit: 40)                              │ │
│  │  • Memory checkpointing                                        │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │ agent.process(state)
                                   │ state updates
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         AGENT MODULE                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │KanoonFetcher │  │DocumentSummar│  │InitialRetriever             │
│  │   Agent      │  │  izer Agent  │  │    Agent     │              │
│  │              │  │              │  │              │              │
│  │• Keyword     │  │• Doc Length  │  │• Query Gen   │              │
│  │  Extraction  │  │  Check       │  │• Multi-source│              │
│  │• API Calls   │  │• LLM Summary │  │  Retrieval   │              │
│  │• File Save   │  │• Compression │  │• RAG System  │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                       │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐              │
│  │Defense Lawyer│  │ Prosecutor   │  │    Judge     │              │
│  │    Agent     │  │    Agent     │  │    Agent     │              │
│  │              │  │              │  │              │              │
│  │• 2-step      │  │• 2-step      │  │• Evaluate    │              │
│  │  Thought     │  │  Thought     │  │• Route Logic │              │
│  │• Citation    │  │• Citation    │  │• Feedback    │              │
│  │  Check       │  │  Check       │  │• Safety Force│              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                       │
│  ┌──────┴───────┐  ┌──────┴───────┐                                 │
│  │Verdict Agent │  │ Web Search   │                                 │
│  │              │  │    Agent     │                                 │
│  │• Transcript  │  │• Serper API  │                                 │
│  │  Analysis    │  │• CrewAI      │                                 │
│  │• 7-part      │  │              │                                 │
│  │  Verdict     │  │              │                                 │
│  └──────────────┘  └──────────────┘                                 │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ retrieve documents
                                   │ verify citations
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         RAG MODULE                                   │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │          Enhanced RAG System (enhanced_rag_system.py)          │ │
│  │                                                                 │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                   │ │
│  │  │ Intelligent      │  │ Citation         │                   │ │
│  │  │ Chunking         │  │ Enforcement      │                   │ │
│  │  │ • 4 regex        │  │ • 4 patterns     │                   │ │
│  │  │   patterns       │  │ • Density 0.15   │                   │ │
│  │  └──────────────────┘  └──────────────────┘                   │ │
│  │                                                                 │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                   │ │
│  │  │ Hallucination    │  │ Legal            │                   │ │
│  │  │ Detection        │  │ Re-Ranking       │                   │ │
│  │  │ • Cosine sim     │  │ • 8 importance   │                   │ │
│  │  │ • Threshold 0.7  │  │   signals        │                   │ │
│  │  └──────────────────┘  └──────────────────┘                   │ │
│  │                                                                 │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                   │ │
│  │  │ Structured       │  │ Context          │                   │ │
│  │  │ Presentation     │  │ Compression      │                   │ │
│  │  │ • 5 categories   │  │ • Max 15K tokens │                   │ │
│  │  │ • Citation tags  │  │ • Importance 5.0x│                   │ │
│  │  └──────────────────┘  └──────────────────┘                   │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │ query vectors
                                   │ store embeddings
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│                       STORAGE MODULE                                 │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              ChromaDB (chroma_store.py)                        │ │
│  │  • PersistentClient with SQLite backend                        │ │
│  │  • Two collections: public + private                           │ │
│  │  • nomic-embed-text embeddings (768-dim)                       │ │
│  │  • HNSW index for ANN search                                   │ │
│  │  • Metadata storage                                            │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL API MODULE                               │
│  ┌──────────────────────┐          ┌──────────────────────┐         │
│  │    Kanoon API        │          │    Serper API        │         │
│  │  • Indian Case Law   │          │  • Web Search        │         │
│  │  • Keyword Query     │          │  • Legal Info        │         │
│  │  • JSON Response     │          │  • Google Results    │         │
│  └──────────────────────┘          └──────────────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Figure 4: RAG Pipeline Flowchart

```
           ┌──────────────────┐
           │  User Query /    │
           │  Case Input      │
           └────────┬─────────┘
                    │
                    ↓
           ┌─────────────────────┐
           │ Keyword Extraction  │
           │ (LLM generates      │
           │  3-5 search queries)│
           └────────┬────────────┘
                    │
                    ↓
           ┌─────────────────────┐
           │  Vector Search      │
           │  (ChromaDB HNSW)    │
           │  • Public docs      │
           │  • Private docs     │
           └────────┬────────────┘
                    │
                    ↓
           ┌─────────────────────┐
           │  BM25 Re-ranking    │
           │  (Keyword overlap   │
           │   scoring)          │
           └────────┬────────────┘
                    │
                    ↓
           ┌─────────────────────┐
           │  Legal Re-ranking   │
           │  Check importance?  │
           └────────┬────────────┘
                    │
          ┌─────────┴─────────┐
          │                   │
          ↓                   ↓
    [IPC Section]      [Case Citation]
      Weight 2.0x        Weight 1.8x
          │                   │
          ↓                   ↓
    [Supreme Court]    [Evidence Mention]
      Weight 2.5x        Weight 1.6x
          │                   │
          └─────────┬─────────┘
                    │
                    ↓
           ┌─────────────────────┐
           │ Context Compression │
           │ Token count > 15K?  │
           └────────┬────────────┘
                    │
          ┌─────────┴─────────┐
          ↓                   ↓
        [YES]               [NO]
          │                   │
          ↓                   │
    ┌──────────────┐          │
    │Assign Import-│          │
    │ance Scores:  │          │
    │• IPC: 5.0x   │          │
    │• Case: 3.0x  │          │
    │• Statute: 4.0x│         │
    │Keep top      │          │
    │sentences     │          │
    └──────┬───────┘          │
           │                  │
           └─────────┬────────┘
                     │
                     ↓
           ┌─────────────────────┐
           │ Structured          │
           │ Presentation        │
           │ Categorize into:    │
           │ • IPC Sections      │
           │ • Case Precedents   │
           │ • Legal Principles  │
           │ • Evidence & Facts  │
           │ • Procedural Law    │
           └────────┬────────────┘
                    │
                    ↓
           ┌─────────────────────┐
           │  Citation Tagging   │
           │  Add markers:       │
           │  [IPC-1], [CAS-2]   │
           │  [DOC-3], [EVI-4]   │
           └────────┬────────────┘
                    │
                    ↓
           ┌─────────────────────┐
           │  Output to Agents   │
           │  (Retrieved Context)│
           └─────────────────────┘
```

---

## Figure 5: State Diagram - Agent Workflow

```
                    ┌─────────────────┐
                    │     START       │
                    └────────┬────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │ Kanoon Fetcher  │
                    │    (Green)      │
                    └────────┬────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │Document Summariz│
                    │      (Green)    │
                    └────────┬────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │Initial Retriever│
                    │     (Green)     │
                    └────────┬────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │  Defense Lawyer │
                    │     (Blue)      │
                    └────────┬────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │      Judge      │
                    │     (Yellow)    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ↓              ↓              ↓
      ┌──────────────┐  ┌─────────┐  ┌──────────┐
      │   Lawyer     │  │Prosecutor│  │ Verdict  │
      │   (Blue)     │  │  (Red)  │  │ (Purple) │
      └──────┬───────┘  └────┬────┘  └────┬─────┘
             │               │            │
             │               │            │
             ↓               ↓            │
      ┌──────────────┐  ┌─────────┐      │
      │    Judge     │  │  Judge  │      │
      │   (Yellow)   │  │(Yellow) │      │
      └──────┬───────┘  └────┬────┘      │
             │               │            │
             │               │            │
             └───────┬───────┘            │
                     │                    │
                     ↓                    │
              ┌────────────┐              │
              │ Iteration  │              │
              │  < 22?     │              │
              └─────┬──────┘              │
                    │                     │
         ┌──────────┴─────────┐           │
         ↓                    ↓           │
       [YES]                [NO]          │
         │                    │           │
         │ Continue           │ Force     │
         │ Debate             │ Verdict   │
         │                    └───────────┘
         │                            │
         └────────────────┐           │
                          │           │
                          ↓           ↓
                    ┌─────────────────┐
                    │    Verdict      │
                    │    (Purple)     │
                    └────────┬────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │      END        │
                    └─────────────────┘

Legend:
━━━ Sequential edge (always follows)
─── Conditional edge (routing decision)

Color Codes:
Blue     = Defense Lawyer
Red      = Prosecutor
Yellow   = Judge
Purple   = Verdict
Green    = Utility Agents
```

---

## Figure 6: Citation Verification Flowchart

```
           ┌──────────────────────┐
           │   Agent Response     │
           │   (Text Output)      │
           └──────────┬───────────┘
                      │
                      ↓
           ┌──────────────────────┐
           │  Extract Citations   │
           │  Find citation       │
           │  patterns in text    │
           └──────────┬───────────┘
                      │
                      ↓
           ┌──────────────────────────────┐
           │ Pattern Matching (4 types):  │
           │ 1. [XXX-N] format            │
           │ 2. "according to Section X"  │
           │ 3. "in the case of X vs Y"   │
           │ 4. "#DOC-N" references       │
           └──────────┬───────────────────┘
                      │
                      ↓
           ┌──────────────────────┐
           │ Extract Legal        │
           │ Entities:            │
           │ • IPC Section X      │
           │ • CrPC Section Y     │
           │ • Case Name vs Name  │
           │ • Article Z          │
           └──────────┬───────────┘
                      │
                      ↓
           ┌──────────────────────┐
           │  Count Citations     │
           │  total_citations =   │
           │  pattern_matches +   │
           │  entity_mentions     │
           └──────────┬───────────┘
                      │
                      ↓
           ┌──────────────────────┐
           │ Calculate Density    │
           │ density = citations  │
           │          / sentences │
           └──────────┬───────────┘
                      │
                      ↓
           ┌──────────────────────┐
           │ Check Against        │
           │ Retrieved Documents  │
           │ Verify each citation │
           │ exists in context    │
           └──────────┬───────────┘
                      │
                      ↓
           ┌──────────────────────┐
           │  Density < 0.15?     │
           │  (threshold check)   │
           └──────────┬───────────┘
                      │
            ┌─────────┴─────────┐
            ↓                   ↓
          [YES]               [NO]
            │                   │
            ↓                   ↓
  ┌─────────────────┐  ┌──────────────┐
  │Generate Warning:│  │Citation Check│
  │"Low citation    │  │    PASSED    │
  │ density in      │  └──────┬───────┘
  │ response"       │         │
  └────────┬────────┘         │
           │                  │
           └─────────┬────────┘
                     │
                     ↓
           ┌─────────────────────┐
           │ Return Analysis:    │
           │ • citation_count    │
           │ • entity_count      │
           │ • density           │
           │ • verification_rate │
           │ • warnings[]        │
           └─────────────────────┘
```

---

## Figure 7: Document Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     STAGE 1: INGESTION                          │
│                                                                 │
│  ┌─────┐  ┌─────┐  ┌─────┐                                    │
│  │ PDF │  │DOCX │  │ TXT │  ← Document Files                  │
│  └──┬──┘  └──┬──┘  └──┬──┘                                    │
│     │        │        │                                        │
│     ↓        ↓        ↓                                        │
│  ┌──────────────────────┐                                     │
│  │  Document Loaders:   │                                     │
│  │  • PyMuPDFLoader     │                                     │
│  │  • Docx2txtLoader    │                                     │
│  │  • TextLoader        │                                     │
│  └──────────┬───────────┘                                     │
│             │                                                  │
│             ↓                                                  │
│  ┌────────────────────────┐                                   │
│  │ Document Objects with: │                                   │
│  │ • page_content         │                                   │
│  │ • metadata (source)    │                                   │
│  └──────────┬─────────────┘                                   │
└─────────────┼──────────────────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     STAGE 2: CHUNKING                           │
│                                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │   IntelligentChunker                   │                    │
│  │   Detect structure with 4 regex:       │                    │
│  │   1. Section/Article/Rule \d+         │                    │
│  │   2. IPC/CrPC/CPC Section \d+         │                    │
│  │   3. Numbered lists (\d+|\[A-Z\])     │                    │
│  │   4. Case names: X vs Y                │                    │
│  └────────────┬───────────────────────────┘                    │
│               │                                                 │
│               ↓                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │ Split by sections                      │                    │
│  │ chunk_size = 1000                      │                    │
│  │ chunk_overlap = 200                    │                    │
│  │ Preserve section_header metadata       │                    │
│  └────────────┬───────────────────────────┘                    │
│               │                                                 │
│               ↓                                                 │
│  ┌────────────────────┐                                        │
│  │  Document Chunks   │                                        │
│  │  with metadata     │                                        │
│  └────────────┬───────┘                                        │
└───────────────┼──────────────────────────────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────────────────────────────┐
│                     STAGE 3: EMBEDDING                          │
│                                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │   OllamaEmbeddings                     │                    │
│  │   Model: nomic-embed-text              │                    │
│  │   Dimensions: 768                      │                    │
│  └────────────┬───────────────────────────┘                    │
│               │                                                 │
│               ↓                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │ embed_documents()                      │                    │
│  │ • Normalize to unit length             │                    │
│  │ • Batch processing                     │                    │
│  └────────────┬───────────────────────────┘                    │
│               │                                                 │
│               ↓                                                 │
│  ┌─────────────────────────────┐                               │
│  │  Embedding Vectors          │                               │
│  │  [768-dimensional arrays]   │                               │
│  └────────────┬────────────────┘                               │
└───────────────┼──────────────────────────────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────────────────────────────┐
│                     STAGE 4: STORAGE                            │
│                                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │   ChromaDB PersistentClient            │                    │
│  │   Backend: SQLite                      │                    │
│  │   Index: HNSW (ANN search)             │                    │
│  └────────────┬───────────────────────────┘                    │
│               │                                                 │
│               ↓                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │ Create Collections:                    │                    │
│  │ • public_documents_collection          │                    │
│  │ • private_documents_collection         │                    │
│  └────────────┬───────────────────────────┘                    │
│               │                                                 │
│               ↓                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │ Store:                                 │                    │
│  │ • Document ID (hash)                   │                    │
│  │ • Embedding vector                     │                    │
│  │ • Metadata (source, section_header)    │                    │
│  │ • Original text                        │                    │
│  └────────────┬───────────────────────────┘                    │
└───────────────┼──────────────────────────────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────────────────────────────┐
│                     STAGE 5: RETRIEVAL                          │
│                                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │  Query Input                           │                    │
│  └────────────┬───────────────────────────┘                    │
│               │                                                 │
│               ↓                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │  embed_query()                         │                    │
│  │  Convert query to 768-dim vector       │                    │
│  └────────────┬───────────────────────────┘                    │
│               │                                                 │
│               ↓                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │  HNSW Index Search                     │                    │
│  │  • Find k nearest neighbors            │                    │
│  │  • Cosine similarity scoring           │                    │
│  └────────────┬───────────────────────────┘                    │
│               │                                                 │
│               ↓                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │  Retrieved Documents                   │                    │
│  │  Sorted by similarity (descending)     │                    │
│  └────────────┬───────────────────────────┘                    │
└───────────────┼──────────────────────────────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────────────────────────────┐
│                     STAGE 6: RE-RANKING                         │
│                                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │   LegalReRanker                        │                    │
│  │   Score with importance signals:       │                    │
│  │   • Supreme Court: 2.5x                │                    │
│  │   • IPC Section: 2.0x                  │                    │
│  │   • High Court: 2.0x                   │                    │
│  │   • Case Law: 1.8x                     │                    │
│  │   • Punishment: 1.7x                   │                    │
│  │   • Evidence: 1.6x                     │                    │
│  │   • Definition: 1.5x                   │                    │
│  └────────────┬───────────────────────────┘                    │
│               │                                                 │
│               ↓                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │   ContextCompressor                    │                    │
│  │   • Reduce to max_tokens (15000)       │                    │
│  │   • Preserve high-importance sentences │                    │
│  └────────────┬───────────────────────────┘                    │
│               │                                                 │
│               ↓                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │   StructuredPresenter                  │                    │
│  │   Categorize and format:               │                    │
│  │   • [IPC-1], [CAS-2], [DOC-3]         │                    │
│  │   • Group by category                  │                    │
│  └────────────┬───────────────────────────┘                    │
│               │                                                 │
│               ↓                                                 │
│  ┌────────────────────────────────────────┐                    │
│  │  Final Retrieved Context               │                    │
│  │  Ready for Agent Consumption           │                    │
│  └────────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Figure 8: Citation Statistics Bar Chart (Text Representation)

```
Average Citations per Response by Agent Type

                    ┌────────────────────────────────────────┐
                    │                                        │
                    │  ■ Direct Citations [XXX-N]            │
                    │  ■ Legal Entity Mentions               │
                    │  ■ Total References                    │
                    │                                        │
                    └────────────────────────────────────────┘

    8 │
      │
    7 │                                    ███████
      │                                    ███████
    6 │                        ███████     ███████
      │                        ███████     ███████
    5 │         ███████        ███████     ███████
      │         ███████        ███████     ███████
    4 │         ███████        ███████     ███████
      │         ███████        ███████     ███████     ███████
    3 │         ███████        ███████     ███████     ███████
      │  ─────  ███████ ─────  ███████     ███████     ███████
    2 │  ▓▓▓▓▓  ███████ ▓▓▓▓▓  ███████     ███████     ███████
      │  ▓▓▓▓▓  ███████ ▓▓▓▓▓  ███████     ███████     ███████
    1 │  ▓▓▓▓▓  ███████ ▓▓▓▓▓  ███████     ███████     ███████
      │  ▓▓▓▓▓  ███████ ▓▓▓▓▓  ███████  ─────────────  ███████
    0 │__▓▓▓▓▓__███████_▓▓▓▓▓__███████_____█████_______███████____
      │  ░░░░░  ░░░░░░░ ░░░░░  ░░░░░░░     ░░░░░       ░░░░░░░
          │        │       │        │          │           │
       Lawyer   Lawyer  Prosec.  Prosec.    Judge       Judge
       Direct   Total   Direct   Total      Direct      Total


    Legend:
    ░░░░░  Direct Citations [IPC-1], [CAS-2] format
    ▓▓▓▓▓  Legal Entity Mentions (IPC Section X, Case Y vs Z)
    █████  Total References (Direct + Entities)
    ─────  No data for this category


    Summary Statistics:
    ┌────────────────┬────────────┬─────────────┬────────────────┐
    │ Agent Type     │   Direct   │   Entities  │ Total Refs     │
    ├────────────────┼────────────┼─────────────┼────────────────┤
    │ Defense Lawyer │    3.2     │     1.8     │      5.0       │
    │ Prosecutor     │    4.1     │     2.5     │      6.6       │
    │ Judge          │    1.5     │     0.8     │      2.3       │
    └────────────────┴────────────┴─────────────┴────────────────┘

    Citation Density:
    - Lawyer:     0.18 citations/sentence
    - Prosecutor: 0.22 citations/sentence
    - Judge:      0.12 citations/sentence

    System Average: 0.20 citations/sentence (Target: > 0.15)
```

---

## Figure 9: State vs. Rohan Malhotra - Trial Timeline

```
Trial Progression: State vs. Rohan Malhotra (Defamation + Cyber Harassment)
Total Iterations: 16 | Duration: ~6 minutes | Verdict: NOT GUILTY

Iteration Timeline:
═══════════════════════════════════════════════════════════════════════════

Iter 1-3: CASE PREPARATION PHASE
├─ [1] Kanoon Fetcher      ░░░░░░░░░░░░░░░░ Keyword extraction
│   Keywords: "defamation IPC 499", "cyber harassment IT Act",
│             "account hacking defense", "social media evidence"
│   Result: 8 relevant cases fetched
│
├─ [2] Document Summarizer ░░░░░░░░░░░░░░░░ Compression: 73%
│   Large docs compressed while preserving key citations
│
└─ [3] Initial Retriever   ░░░░░░░░░░░░░░░░ RAG retrieval
    Retrieved: 12 IPC sections, 15 case precedents
    Citation markers created: [IPC-1] to [IPC-12], [CAS-1] to [CAS-15]

═══════════════════════════════════════════════════════════════════════════

Iter 4-5: OPENING STATEMENTS
├─ [4] Defense Lawyer      ████████████████ Opening Statement
│   Key Arguments:
│   • Lack of mens rea (criminal intent) [IPC-499]
│   • Technical evidence of account compromise
│   • Character evidence of defendant
│   • Burden of proof on prosecution
│   Citations: 4 direct, 3 entity mentions
│   Confidence: ▓▓▓▓▓▓░░░░ 65%
│
└─ [5] Judge               ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ Evaluation
    Assessment: "Defense presents technical evidence. Prosecution must
                 address account compromise claims."
    Routing: → Prosecutor

═══════════════════════════════════════════════════════════════════════════

Iter 6-14: ARGUMENT & REBUTTAL PHASE

[6] Prosecutor            ████████████████ Initial Response
    • Account ownership responsibility
    • Timing correlation with business dispute
    • No immediate reporting of compromise
    Citations: 5 direct, 2 entities
    Confidence: ▓▓▓▓▓▓▓░░░ 70%

[7] Judge                 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ Feedback + Routing → Lawyer

[8] Defense Lawyer        ████████████████ Rebuttal #1
    ⚡ KEY MOMENT: Foreign IP Evidence Presented
    • Login logs show foreign IP addresses
    • Unusual access patterns documented
    • Timeline doesn't match defendant's location
    Citations: 6 direct, 4 entities
    Confidence: ▓▓▓▓▓▓▓▓░░ 75%

[9] Judge                 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ "Strong technical evidence"
    Routing: → Prosecutor

[10] Prosecutor           ████████████████ Counter-argument
     • Questions reliability of technical logs
     • Argues post-hoc fabrication possible
     ⚠️  Judge Warning: "Lacks case law support for this claim"
     Citations: 3 direct, 2 entities
     Confidence: ▓▓▓▓▓░░░░ 55%

[11] Judge                ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ Citation gap identified
     Routing: → Lawyer

[12] Defense Lawyer       ████████████████ Closing Arguments Begin
     ⚡ KEY MOMENT: Reasonable Doubt Established
     • Comprehensive review of technical evidence
     • Cites IT Act provisions on digital evidence
     • References precedents on mens rea requirement
     Citations: 7 direct, 5 entities
     Confidence: ▓▓▓▓▓▓▓▓▓░ 82%

[13] Judge                ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ "Prosecution must address doubt"
     Routing: → Prosecutor

[14] Prosecutor           ████████████████ Final Arguments
     • Attempts narrow construction argument
     • Argues circumstantial evidence sufficient
     • Last effort to save case
     Citations: 4 direct, 3 entities
     Confidence: ▓▓▓▓▓▓░░░ 60%

═══════════════════════════════════════════════════════════════════════════

Iter 15-16: VERDICT PHASE

[15] Judge                ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ Final Assessment
     Iteration 15 reached. Case ready for verdict.
     Routing: → Verdict Agent

[16] Verdict Agent        ████████████████ FINAL VERDICT
     ╔════════════════════════════════════════════════════════╗
     ║           VERDICT: NOT GUILTY                          ║
     ╚════════════════════════════════════════════════════════╝

     Reasoning:
     1. Prosecution failed to prove mens rea beyond reasonable doubt
     2. Technical evidence (foreign IPs, unusual patterns) not rebutted
     3. Defense established plausible alternative explanation
     4. IPC Section 499 requires criminal intent - not established
     5. IT Act provisions support account compromise defense

     Confidence: ▓▓▓▓▓▓▓░░░ 72%

     Evidence Analysis:
     ✓ Technical logs favor defense
     ✓ Timeline inconsistencies support compromise claim
     ✗ Prosecution lacked strong rebuttal evidence

     Legal Arguments Assessment:
     Defense: Strong legal foundation with proper citations
     Prosecution: Circumstantial, insufficient to overcome doubt

═══════════════════════════════════════════════════════════════════════════

Confidence Evolution Graph:

100%│
    │
 90%│
    │
 80%│                                            ╱─╲
    │                                       ╱───╯   ╲
 70%│                   ╱───╲         ╱───╯          ╲
    │              ╱───╯     ╲───╱───╯                ╲─╮
 60%│         ╱───╯               ╲                     ╰╮
    │    ╱───╯                     ╲                     ╰─╮
 50%│───╯                                                   ╰──
    │
 40%│
    └─────────────────────────────────────────────────────────
     1   3   5   7   9   11  13  15  16
     │   │   │   │   │   │   │   │   │
    Prep Open Arg1 Rbt1 Rbt2 Cls1 Cls2 Verd

Legend:
░░░░ Preparation/Utility   ████ Defense Lawyer
▒▒▒▒ Judge                 ████ Prosecutor
⚡ Key turning point       ▓▓▓▓ Confidence level (visual)
```
