# Image Placeholder Reference Guide

This document provides detailed specifications for all 11 images needed in the report.

## Figure 1: System Architecture Diagram
**Location:** Section 3.1 (Analysis - System Architecture)

**Description:**
- **Type:** Layered architecture diagram
- **Layers (top to bottom):**
  1. User (stick figure icon at top)
  2. Presentation Layer: Streamlit UI (purple box)
  3. Application Layer: FastAPI + SSE (blue box)
  4. Orchestration Layer: LangGraph Workflow (green box)
  5. Agent Layer: 8 agent boxes (LawyerAgent, ProsecutorAgent, JudgeAgent, VerdictAgent, InitialRetrieverAgent, KanoonFetcherAgent, WebSearcherAgent, DocumentSummarizationAgent)
  6. RAG System: Enhanced RAG box (orange)
  7. Data Layer: ChromaDB (yellow box at bottom)
- **Side elements:** 
  - Kanoon API (cloud icon, right side)
  - Serper API (cloud icon, right side)
- **Arrows:** Show data flow between all layers with labels like "User Request", "Stream Events", "Agent Calls", "Retrieve Docs"
- **Colors:** Use distinct colors for each layer
- **Size:** Full page width

## Figure 2: Multi-Agent Workflow Graph
**Location:** Section 3.2 (Analysis - Multi-Agent Workflow)

**Description:**
- **Type:** Flow diagram with stages
- **Elements:**
  - Rectangle boxes for each agent
  - Arrows showing sequence
  - Loop indicator for lawyer-prosecutor-judge cycle
  - Decision diamond for judge routing
- **Flow:**
  1. START → KanoonFetcher
  2. KanoonFetcher → DocumentSummarizer
  3. DocumentSummarizer → InitialRetriever
  4. InitialRetriever → Lawyer (opening statement)
  5. Lawyer ↔ Prosecutor ↔ Judge (iteration loop with curved arrow)
  6. Judge → Verdict (decision point)
  7. Verdict → END
- **Annotations:** Label each stage (Stage 1: Case Preparation, Stage 2: Initial Retrieval, Stage 3: Trial Proceedings, Stage 4: Verdict)
- **Colors:** 
  - Green for preparation agents
  - Blue for lawyer
  - Red for prosecutor
  - Yellow for judge
  - Purple for verdict
- **Size:** Full page width

## Figure 3: Agent Interaction Sequence
**Location:** Section 3.3 (Analysis - Agent Interaction Sequence)

**Description:**
- **Type:** UML-style sequence diagram
- **Participants (vertical lines):** User, Lawyer, Prosecutor, Judge, Verdict
- **Messages (horizontal arrows):**
  - User → Lawyer: "Case Description"
  - Lawyer → Lawyer: Internal thought steps (box on line)
  - Lawyer → Judge: "Opening Statement [IPC-1]"
  - Judge → Judge: Evaluation (box on line)
  - Judge → Prosecutor: "Your turn"
  - Prosecutor → Prosecutor: Thought steps (box on line)
  - Prosecutor → Judge: "Rebuttal [CAS-2]"
  - Judge → Lawyer: "Response needed"
  - (Repeat 3-4 times)
  - Judge → Verdict: "Ready for verdict"
  - Verdict → User: "Final Decision"
- **Boxes:** Show internal processing with dashed borders
- **Iteration:** Use a loop frame around the lawyer-prosecutor-judge exchanges labeled "Repeat 15-20 times"
- **Size:** Full page height

## Figure 4: Web Interface Screenshot
**Location:** Section 5.2 (Results - Web Interface)

**Description:**
- **Type:** Mockup of Streamlit interface
- **Header:** 
  - "Lex Simulacra - AI Courtroom Simulator" title
  - Scales of justice icon (⚖️)
  - Purple gradient background
- **Sidebar (left, 30% width):**
  - "Case Input" text area (with sample text visible)
  - "Upload Documents" file upload button
  - "Start Simulation" button (purple)
- **Main Area (right, 70% width):**
  - **Timeline panel (narrow left column):**
    - Vertical timeline with dots
    - Labels: "Kanoon Fetch", "Lawyer", "Prosecutor", "Judge", etc.
  - **Agent Cards (main area):**
    - Blue card: "DEFENSE LAWYER" with sample argument text
    - Red card: "PROSECUTOR" with sample rebuttal text
    - Yellow card: "JUDGE" with sample feedback text
    - Green card: "VERDICT" with "NOT GUILTY" prominent
  - Each card has rounded corners and shadow
- **Bottom Metrics Bar:**
  - "Iterations: 15"
  - "Citations: 24"
  - "Confidence: 78%"
- **Style:** Clean, modern UI with good spacing
- **Size:** Landscape orientation, full page width

## Figure 5: RAG Pipeline Flow
**Location:** Section 4.2 (Design - Enhanced RAG System)

**Description:**
- **Type:** Detailed flowchart
- **Boxes (left to right):**
  1. "Query Input" (oval)
  2. "Keyword Extraction" (rectangle)
  3. "Vector Search" (rectangle with database icon)
  4. "BM25 Re-ranking" (rectangle)
  5. "Legal Re-ranking" (rectangle, highlighted)
  6. Decision Diamond: "Context > 18K tokens?"
     - Yes → "Context Compression" box
     - No → Skip to next
  7. "Structuring by Category" (rectangle)
  8. "Citation Tagging" (rectangle)
  9. "Output to Agents" (oval)
- **Arrows:** Connect all boxes with labels
- **Annotations:** 
  - Under "Legal Re-ranking": "IPC: 2.0x, SC Cases: 2.5x"
  - Under "Compression": "Preserve IPC: 5.0x, Cases: 3.0x"
  - Under "Structuring": "IPC Sections | Case Precedents | Evidence"
- **Colors:** Use orange for highlighted legal steps
- **Size:** Full page width

## Figure 6: State Diagram
**Location:** Section 4.4 (Design - Workflow Graph Implementation)

**Description:**
- **Type:** State machine diagram
- **States (circles with labels):**
  - START (double circle)
  - KanoonFetcher
  - DocumentSummarizer
  - InitialRetriever
  - Lawyer
  - Prosecutor
  - Judge
  - Verdict
  - END (double circle)
- **Transitions (directed arrows):**
  - Single edges: START→Kanoon, Kanoon→Summarizer, Summarizer→Retriever, Retriever→Lawyer
  - Conditional edges from Judge:
    - Judge → Lawyer (labeled "continue_debate, next=lawyer")
    - Judge → Prosecutor (labeled "continue_debate, next=prosecutor")
    - Judge → Verdict (labeled "end_debate")
  - Lawyer/Prosecutor self-loops (labeled "thought_step")
  - Verdict → END
- **Colors:**
  - Green: Preparation states
  - Blue: Lawyer
  - Red: Prosecutor
  - Yellow: Judge
  - Purple: Verdict
- **Size:** Full page width

## Figure 7: Citation Enforcement Mechanism
**Location:** Section 4.5 (Design - Citation Enforcement)

**Description:**
- **Type:** Process flowchart
- **Steps:**
  1. "Agent Response" (input, rectangle)
  2. "Extract Citations" (process, rectangle)
  3. "Pattern Matching" (decision diamond: "Found [XXX-N]?")
     - Yes → Continue
     - No → "Warning: No citations"
  4. "Extract Legal Entities" (process)
  5. "Find: IPC Section X, Case vs Case" (subprocess box)
  6. "Count Citations" (process)
  7. "Calculate Density" (process, formula: citations/sentences)
  8. "Check Against Retrieved Docs" (decision diamond: "All citations valid?")
     - Yes → "Pass"
     - No → "Warning: Invalid citation"
  9. "Return Analysis" (output, rectangle with fields: citation_count, legal_entity_count, density, warnings)
- **Colors:** 
  - Green for pass
  - Red for warnings
  - Blue for processing
- **Size:** Full page width

## Figure 8: Document Processing Pipeline
**Location:** Section 4.6 (Design - Document Processing Pipeline)

**Description:**
- **Type:** Linear pipeline diagram
- **Stages (left to right with icons):**
  1. **Ingestion:** Document icons (PDF, DOCX, TXT files)
  2. **Chunking:** Scissors icon cutting document, label "IntelligentChunker - Preserve Sections"
  3. **Embedding:** Neural network icon, label "Sentence Transformers"
  4. **Storage:** Database icon (cylinder), label "ChromaDB + Metadata"
  5. **Retrieval:** Magnifying glass icon, label "Cosine Similarity Search"
  6. **Re-ranking:** Trophy icon, label "Legal Importance Weights"
- **Arrows:** Large arrows between stages
- **Annotations:**
  - Under Chunking: "IPC sections, Case boundaries"
  - Under Storage: "Source, Headers, Type"
  - Under Re-ranking: "IPC: 2.0x, SC: 2.5x"
- **Colors:** Gradient from blue (input) to green (output)
- **Size:** Full page width

## Figure 9: Citation Statistics Bar Chart
**Location:** Section 5.5 (Results - Citation Analysis)

**Description:**
- **Type:** Grouped bar chart
- **X-axis:** Agent types (Lawyer, Prosecutor, Judge)
- **Y-axis:** Average citations per response (0-10 scale)
- **Bars (grouped by agent):**
  - Blue bar: Direct Citations ([IPC-X], [CAS-Y])
    - Lawyer: 3-5
    - Prosecutor: 4-6
    - Judge: 1-2
  - Orange bar: Legal Entity Mentions (IPC Section X, Case vs Case)
    - Lawyer: 5-7
    - Prosecutor: 6-8
    - Judge: 2-3
  - Green bar: Total References (sum of above)
    - Lawyer: 8-12
    - Prosecutor: 10-14
    - Judge: 3-5
- **Legend:** Top right corner
- **Title:** "Citation Analysis by Agent Type"
- **Grid:** Horizontal grid lines for readability
- **Size:** Half page width

## Figure 10: Case Timeline Visualization
**Location:** Section 5.7 (Results - Real Case Study)

**Description:**
- **Type:** Combined timeline and line graph
- **X-axis:** Iteration number (1-16)
- **Y-axis (left):** Agent type
- **Y-axis (right):** Confidence percentage (0-100%)
- **Timeline elements (colored horizontal bars):**
  - Iterations 1-3: Green bars (Kanoon, Summarizer, Retriever)
  - Iteration 4: Blue bar (Lawyer opening)
  - Iteration 5: Red bar (Prosecutor response)
  - Iteration 6-7: Yellow bars (Judge evaluation)
  - Iterations 8-15: Alternating blue/red bars (arguments) with yellow separators
  - Iteration 16: Purple bar (Verdict)
- **Annotations on bars:**
  - Iteration 4: "Account Compromise Defense"
  - Iteration 5: "Ownership Responsibility"
  - Iteration 9: "Judge Identifies Citation Gap"
  - Iteration 12: "Technical Evidence Presented"
  - Iteration 16: "NOT GUILTY - 72% Confidence"
- **Overlaid line graph:** 
  - Red line showing confidence evolution
  - Starts at ~30% (iteration 1)
  - Fluctuates between 40-60% (iterations 4-14)
  - Rises to 72% at verdict (iteration 16)
- **Size:** Full page width

## Figure 11: Production Readiness Dashboard
**Location:** Section 5.8 (Results - Production Readiness)

**Description:**
- **Type:** Dashboard with multiple metrics
- **Layout:** 2x2 grid
- **Quadrant 1 (top-left): Case Success Rate**
  - Pie chart: 95% success (green), 5% edge cases (yellow)
  - Label: "High-Quality Results"
- **Quadrant 2 (top-right): Hallucination Detection**
  - Gauge meter: 94% success rate
  - Color gradient: red (0%) → yellow (50%) → green (100%)
  - Needle pointing to 94%
- **Quadrant 3 (bottom-left): Performance Stability**
  - Line graph: Memory usage over time (stable at 2-3 GB)
  - X-axis: Case complexity
  - Y-axis: Memory (GB)
- **Quadrant 4 (bottom-right): Citation Discipline**
  - Horizontal bar: 0.20 average density
  - Scale: 0.0 to 0.30
  - Bar filled to 0.20 (67%), colored green
- **Title:** "Production Readiness Metrics"
- **Footer:** "System Status: READY FOR DEPLOYMENT"
- **Size:** Full page width

---

## Creation Tools Recommendations

1. **Architecture & Flowcharts (Figures 1, 2, 5, 7, 8):**
   - draw.io (free, web-based)
   - Lucidchart
   - Microsoft Visio
   - PlantUML (code-based)

2. **Sequence Diagram (Figure 3):**
   - PlantUML
   - Mermaid
   - SequenceDiagram.org

3. **State Diagram (Figure 6):**
   - draw.io
   - GraphViz
   - PlantUML

4. **UI Mockup (Figure 4):**
   - Figma
   - Adobe XD
   - Canva
   - Screenshot editing tools

5. **Charts (Figures 9, 10, 11):**
   - Microsoft Excel
   - Python matplotlib/seaborn
   - Google Sheets
   - Tableau

## Export Guidelines

- **Format:** PNG or PDF (vector preferred)
- **Resolution:** 300 DPI minimum
- **Naming:** `figure_X_description.png` (e.g., `figure_1_system_architecture.png`)
- **Size:** Width should fit within LaTeX margins (approximately 6 inches)
- **Colors:** Use professional color palette, avoid overly bright colors
- **Text:** Ensure all text is readable at report size (minimum 10pt font)

## LaTeX Integration

Once images are created, replace placeholders with:
```latex
\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{figure_1_system_architecture.png}
\caption{System Architecture Diagram}
\label{fig:system_architecture}
\end{figure}
```

Place image files in the same directory as `synopsis_generated.tex` or create an `images/` subdirectory and adjust paths accordingly.
