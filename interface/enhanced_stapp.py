import streamlit as st
import json
import re
from pathlib import Path
from datetime import datetime
import requests
import time

# Page configuration
st.set_page_config(
    page_title="Lex Simulacra - AI Courtroom Simulator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f1f1f;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5em;
    }
    
    .main-header p {
        color: #f0f0f0;
        margin: 5px 0 0 0;
    }
    
    .agent-card {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    
    .agent-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .judge-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    .prosecutor-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #1f1f1f;
    }
    
    .lawyer-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: #1f1f1f;
    }
    
    .retriever-card, .kanoon-card, .web-card, .summarizer-card, .initial-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: #1f1f1f;
    }
    
    .verdict-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    .agent-name {
        font-size: 1.3em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .agent-message {
        margin-top: 10px;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    
    .timeline-item {
        padding: 10px;
        margin: 5px 0;
        border-left: 3px solid #667eea;
        background: #f8f9fa;
        border-radius: 5px;
        color: #1f1f1f;
    }
    
    .status-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.9em;
        font-weight: bold;
        margin: 5px 0;
    }
    
    .status-running {
        background: #ffc107;
        color: #1f1f1f;
    }
    
    .status-complete {
        background: #28a745;
        color: white;
    }
    
    .iteration-badge {
        background: #6c757d;
        color: white;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.8em;
        margin-left: 10px;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        font-size: 1.1em;
        font-weight: bold;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .metric-container {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        font-size: 0.9em;
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'workflow_started' not in st.session_state:
    st.session_state.workflow_started = False
if 'messages_history' not in st.session_state:
    st.session_state.messages_history = []
if 'timeline' not in st.session_state:
    st.session_state.timeline = []
if 'current_iteration' not in st.session_state:
    st.session_state.current_iteration = 0
if 'total_agents_called' not in st.session_state:
    st.session_state.total_agents_called = 0

# Create directories
UPLOAD_DIR = Path("private_documents")
UPLOAD_DIR.mkdir(exist_ok=True)

def get_agent_icon(agent_name):
    """Return emoji icon for each agent type"""
    icons = {
        "judge": "👨‍⚖️",
        "prosecutor": "👔",
        "lawyer": "🧑‍💼",
        "retriever": "📚",
        "initial_retriever": "🔍",
        "kanoon_fetcher": "⚖️",
        "web_searcher": "🌐",
        "document_summarizer": "📄",
        "verdict": "⚖️"
    }
    return icons.get(agent_name, "🤖")

def get_agent_card_class(agent_name):
    """Return CSS class for agent card styling"""
    classes = {
        "judge": "judge-card",
        "prosecutor": "prosecutor-card",
        "lawyer": "lawyer-card",
        "retriever": "retriever-card",
        "initial_retriever": "initial-card",
        "kanoon_fetcher": "kanoon-card",
        "web_searcher": "web-card",
        "document_summarizer": "summarizer-card",
        "verdict": "verdict-card"
    }
    return classes.get(agent_name, "agent-card")

def format_agent_name(agent_name):
    """Format agent name for display"""
    names = {
        "judge": "Judge",
        "prosecutor": "Prosecutor",
        "lawyer": "Defense Lawyer",
        "retriever": "Legal Retriever",
        "initial_retriever": "Initial Document Retriever",
        "kanoon_fetcher": "Kanoon Case Fetcher",
        "web_searcher": "Web Researcher",
        "document_summarizer": "Document Summarizer",
        "verdict": "Final Verdict"
    }
    return names.get(agent_name, agent_name.title())

# Header
st.markdown("""
<div class="main-header">
    <h1>⚖️ Lex Simulacra</h1>
    <p>AI-Powered Legal Courtroom Simulator</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📁 Case Documents")
    
    uploaded_files = st.file_uploader(
        "Upload case-related documents",
        accept_multiple_files=True,
        type=['pdf', 'txt', 'doc', 'docx'],
        help="Upload any relevant documents for the case"
    )
    
    # Handle file uploads
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        for uploaded_file in uploaded_files:
            file_path = UPLOAD_DIR / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.info(f"📄 {uploaded_file.name}")
    
    st.divider()
    
    # Workflow metrics - using placeholders for real-time updates
    st.header("📊 Simulation Metrics")
    
    metrics_placeholder = st.empty()
    
    # Initial metrics display
    with metrics_placeholder.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{st.session_state.current_iteration}</div>
                <div class="metric-label">Iteration</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{st.session_state.total_agents_called}</div>
                <div class="metric-label">Agents Called</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Timeline - using placeholder for real-time updates
    st.header("⏱️ Timeline")
    timeline_placeholder = st.empty()
    
    # Initial timeline display
    with timeline_placeholder.container():
        if st.session_state.timeline:
            for item in st.session_state.timeline[-10:]:  # Show last 10 items
                st.markdown(f"""
                <div class="timeline-item">
                    <strong>{item['agent']}</strong><br>
                    <small>{item['time']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Timeline will appear here during simulation")

# Main content area
tab1, tab2, tab3 = st.tabs(["🎯 Case Input", "🏛️ Live Courtroom", "📋 Full Transcript"])

with tab1:
    st.header("Enter Case Details")
    
    user_prompt = st.text_area(
        "Case Description",
        value="""Case File

Case Title
State vs. Rohan Malhotra

Case Summary
Rohan Malhotra, a 28-year-old entrepreneur, is accused of defamation under Section 499 of the Indian Penal Code (IPC) and cyber harassment under the Information Technology Act, 2000. The case pertains to Rohan allegedly posting defamatory and harassing statements about Meera Sharma, a 30-year-old journalist, on social media platforms. Rohan denies the charges, claiming his account was hacked at the time the posts were made.

Case Details
Incident Description:
On May 20, 2024, Meera Sharma filed a complaint with the cybercrime division, alleging that Rohan Malhotra made a series of defamatory posts about her on Twitter and Instagram. The posts accused Meera of biased reporting, bribery, and professional misconduct, damaging her reputation among peers and the public.
Rohan Malhotra has stated that he did not make the posts and believes his accounts were compromised. He claims that he noticed suspicious activity on his accounts around the time the posts were made.

Timeline of Events:
May 19, 2024, 8:00 PM: First defamatory tweet posted.
May 19, 2024, 8:30 PM: Instagram story containing similar allegations shared.
May 20, 2024, 9:00 AM: Meera Sharma files a complaint.
May 20, 2024, 11:00 AM: Rohan reports to the cybercrime division, claiming his accounts were hacked.

Evidence:
Screenshots of Posts: Captured by Meera Sharma before they were deleted.
Digital Forensics Report: Analysis of Rohan's devices shows no direct evidence of his involvement but logs indicate suspicious login activity from an unknown IP address.
Witness Testimony: Ravi Verma, a friend of Rohan, states that Rohan mentioned concerns about his social media accounts prior to the incident.
Impact Statement: Meera Sharma has submitted a statement detailing the professional and emotional impact caused by the defamatory posts.

Charges:
Section 499, IPC (Defamation):
Whoever, by words, either spoken or intended to be read, or by signs or visible representations, makes or publishes any imputation concerning any person intending to harm, or knowing or having reason to believe that such imputation will harm, the reputation of such person, is said to defame that person.

Section 66A, IT Act (Cyber Harassment):
Punishment for sending offensive messages through communication service, etc., which cause annoyance or insult.
""",
        height=400,
        help="Enter the complete case details including charges, evidence, and timeline"
    )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Courtroom Simulation", disabled=st.session_state.workflow_started):
            if not user_prompt.strip():
                st.error("❌ Please enter case details before starting the simulation")
            else:
                st.session_state.workflow_started = True
                st.session_state.messages_history = []
                st.session_state.timeline = []
                st.session_state.current_iteration = 0
                st.session_state.total_agents_called = 0
                st.rerun()

with tab2:
    st.header("Live Courtroom Proceedings")
    
    if st.session_state.workflow_started:
        # Create placeholder containers
        status_placeholder = st.empty()
        agent_display = st.empty()
        progress_bar = st.progress(0)
        
        status_placeholder.markdown('<span class="status-badge status-running">🔄 Simulation Running...</span>', unsafe_allow_html=True)
        
        # Use synchronous requests with timeout
        import requests
        import time
        
        url = "http://localhost:8000/stream_workflow"
        
        try:
            # Start time for progress tracking
            start_time = time.time()
            max_time = 1800  # 30 minutes timeout
            
            # Send request with streaming
            response = requests.post(url, json={"user_prompt": user_prompt}, stream=True, timeout=max_time)
            
            if response.status_code != 200:
                st.error(f"❌ Backend error: {response.status_code}")
                st.session_state.workflow_started = False
            else:
                event_count = 0
                
                # Process stream line by line
                for line in response.iter_lines():
                    if line:
                        event_count += 1
                        elapsed = time.time() - start_time
                        
                        # Update progress bar based on time (rough estimate)
                        progress = min(int((elapsed / 600) * 100), 99)  # Cap at 99% until done
                        progress_bar.progress(progress)
                        
                        line_text = line.decode('utf-8')
                        
                        if line_text.startswith('data: '):
                            try:
                                parsed_data = json.loads(line_text[6:])
                                
                                agent_name = parsed_data.get("agent_name", "unknown")
                                agent_message = parsed_data.get("agent_message", "")
                                iteration = parsed_data.get("iteration", 0)
                                next_agent = parsed_data.get("next_agent", "")
                                status = parsed_data.get("status", "progress")
                                
                                # Update metrics in session state
                                st.session_state.current_iteration = iteration
                                st.session_state.total_agents_called += 1
                                
                                # Add to timeline
                                st.session_state.timeline.append({
                                    'agent': format_agent_name(agent_name),
                                    'time': datetime.now().strftime("%H:%M:%S")
                                })
                                
                                # Update metrics in sidebar in real-time
                                with metrics_placeholder.container():
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown(f"""
                                        <div class="metric-container">
                                            <div class="metric-value">{st.session_state.current_iteration}</div>
                                            <div class="metric-label">Iteration</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    with col2:
                                        st.markdown(f"""
                                        <div class="metric-container">
                                            <div class="metric-value">{st.session_state.total_agents_called}</div>
                                            <div class="metric-label">Agents Called</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                # Update timeline in sidebar in real-time
                                with timeline_placeholder.container():
                                    if st.session_state.timeline:
                                        for item in st.session_state.timeline[-10:]:  # Show last 10 items
                                            st.markdown(f"""
                                            <div class="timeline-item">
                                                <strong>{item['agent']}</strong><br>
                                                <small>{item['time']}</small>
                                            </div>
                                            """, unsafe_allow_html=True)
                                
                                # Add to history
                                st.session_state.messages_history.append({
                                    'agent': agent_name,
                                    'message': agent_message,
                                    'iteration': iteration,
                                    'next_agent': next_agent
                                })
                                
                                # Display current speaker with styling
                                if agent_message and agent_message.strip():
                                    icon = get_agent_icon(agent_name)
                                    card_class = get_agent_card_class(agent_name)
                                    formatted_name = format_agent_name(agent_name)
                                    
                                    # Format message for better readability
                                    formatted_message = agent_message.replace('\n', '<br>')
                                    
                                    agent_display.markdown(f"""
                                    <div class="agent-card {card_class}">
                                        <div class="agent-name">
                                            {icon} {formatted_name}
                                            <span class="iteration-badge">Iteration {iteration}</span>
                                        </div>
                                        <div class="agent-message">{formatted_message}</div>
                                        <div style="margin-top: 10px; font-size: 0.9em; opacity: 0.8;">
                                            ➡️ Next: {format_agent_name(next_agent)}
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Check if workflow is complete - only break on done status
                                if status == "done":
                                    progress_bar.progress(100)
                                    status_placeholder.markdown('<span class="status-badge status-complete">✅ Simulation Complete</span>', unsafe_allow_html=True)
                                    st.session_state.workflow_started = False
                                    st.balloons()
                                    break
                            
                            except json.JSONDecodeError as e:
                                st.warning(f"⚠️ Skipping malformed event: {str(e)[:100]}")
                                continue
                        
                        # Prevent timeout - yield control back to Streamlit
                        if event_count % 5 == 0:  # Every 5 events
                            time.sleep(0.01)  # Small sleep to prevent blocking
                
                # Ensure we mark as complete
                if st.session_state.workflow_started:
                    progress_bar.progress(100)
                    status_placeholder.markdown('<span class="status-badge status-complete">✅ Simulation Complete</span>', unsafe_allow_html=True)
                    st.session_state.workflow_started = False
        
        except requests.exceptions.Timeout:
            st.error("❌ Simulation timed out after 30 minutes")
            st.session_state.workflow_started = False
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Make sure it's running: python app.py")
            st.session_state.workflow_started = False
        except Exception as e:
            st.error(f"❌ Error during simulation: {e}")
            import traceback
            st.code(traceback.format_exc())
            st.session_state.workflow_started = False
    
    else:
        st.info("👈 Go to 'Case Input' tab and click 'Start Courtroom Simulation' to begin")
        
        # Show example of what the courtroom looks like
        st.markdown("### Preview: Courtroom Layout")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="agent-card judge-card">
                <div class="agent-name">👨‍⚖️ Judge</div>
                <div class="agent-message">The judge will moderate the proceedings and ensure fair trial...</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="agent-card prosecutor-card">
                <div class="agent-name">👔 Prosecutor</div>
                <div class="agent-message">The prosecutor will present the case against the defendant...</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="agent-card lawyer-card">
                <div class="agent-name">🧑‍💼 Defense Lawyer</div>
                <div class="agent-message">The defense lawyer will argue for the defendant's innocence...</div>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.header("Complete Transcript")
    
    if st.session_state.messages_history:
        for idx, msg in enumerate(st.session_state.messages_history):
            icon = get_agent_icon(msg['agent'])
            card_class = get_agent_card_class(msg['agent'])
            formatted_name = format_agent_name(msg['agent'])
            
            # Format message
            formatted_message = msg['message'].replace('\n', '<br>')
            
            st.markdown(f"""
            <div class="agent-card {card_class}" style="margin-bottom: 15px;">
                <div class="agent-name">
                    {icon} {formatted_name}
                    <span class="iteration-badge">#{idx + 1} - Iteration {msg['iteration']}</span>
                </div>
                <div class="agent-message">{formatted_message}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Download transcript button
        st.markdown("---")
        transcript_text = "\n\n".join([
            f"{'='*80}\n{format_agent_name(msg['agent'])} (Iteration {msg['iteration']})\n{'='*80}\n{msg['message']}"
            for msg in st.session_state.messages_history
        ])
        
        st.download_button(
            label="📥 Download Full Transcript",
            data=transcript_text,
            file_name=f"courtroom_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    else:
        st.info("The complete transcript will appear here once the simulation starts")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 20px;">
    <p>⚖️ Lex Simulacra - AI Legal Courtroom Simulator</p>
    <p style="font-size: 0.9em;">Powered by LangGraph, Ollama, and Streamlit</p>
</div>
""", unsafe_allow_html=True)
