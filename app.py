from core.workflow import TrialWorkflow
from agents import LawyerAgent, ProsecutorAgent, JudgeAgent, RetrieverAgent, FetchingAgent, WebSearcherAgent
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize Google Gemini LLMs (Cloud-based, fast, cost-effective)
# Get API key from environment
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file")

gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

print("="*80)
print("GOOGLE GEMINI LLM INITIALIZATION")
print("="*80)
print(f"Model: {gemini_model}")
print(f"API Key: {'*' * 20}{google_api_key[-4:] if len(google_api_key) > 4 else '****'}")
print("Cloud-based inference - No local GPU required")
print("Expected performance: <5 minutes per workflow (10x faster than local)")
print("="*80)

# Primary LLM for general use
try:
    llm_0 = ChatGoogleGenerativeAI(
        model=gemini_model,
        google_api_key=google_api_key,
        temperature=0.7,
        convert_system_to_human=True  # Important for Gemini compatibility
    )
    print("Primary LLM initialized successfully")
except Exception as e:
    print(f"ERROR: Failed to initialize Gemini LLM: {e}")
    raise

# Multiple LLM instances for different agents (using same model for consistency)
# Note: Gemini is highly reliable, so we use same model with retry logic instead of fallbacks
llms = [
    ChatGoogleGenerativeAI(
        model=gemini_model,
        google_api_key=google_api_key,
        temperature=0.7,
        convert_system_to_human=True
    ),
    ChatGoogleGenerativeAI(
        model=gemini_model,
        google_api_key=google_api_key,
        temperature=0.8,
        convert_system_to_human=True
    ),
    ChatGoogleGenerativeAI(
        model=gemini_model,
        google_api_key=google_api_key,
        temperature=0.6,
        convert_system_to_human=True
    ),
]

print(f"Fallback LLM instances created: {len(llms)}")
print("="*80)

# Initialize Workflow
print("\nWORKFLOW INITIALIZATION")
print("="*80)
print("Creating agent instances...")
print("  - LawyerAgent")
print("  - ProsecutorAgent")
print("  - JudgeAgent")
print("  - RetrieverAgent")
print("  - FetchingAgent (Kanoon)")
print("  - WebSearcherAgent")

workflow = TrialWorkflow(
    lawyer=LawyerAgent(llms=llms),
    prosecutor=ProsecutorAgent(llms=llms),
    judge=JudgeAgent(llms=llms),
    retriever=RetrieverAgent(llms=llms),
    kanoon_fetcher=FetchingAgent(llms=llms),
    web_searcher=WebSearcherAgent(llm=llm_0),
)

print("All agents initialized successfully")
print("Workflow graph compiled")
print("="*80)

@app.post("/stream_workflow")
async def stream_workflow(user_prompt: str = Body(..., embed=True)):
    print("\n" + "="*80)
    print("NEW API REQUEST RECEIVED")
    print("="*80)
    print(f"Prompt length: {len(user_prompt)} characters")
    print(f"First 200 chars: {user_prompt[:200]}...")
    print("Starting workflow stream...")
    print("="*80)
    
    async def event_generator():
        event_count = 0
        async for state in workflow.run(user_prompt=user_prompt):
            event_count += 1
            print(f"[API] Sending event #{event_count} to client: {state.get('status', 'unknown')}")
            yield f"data: {json.dumps(state)}\n\n"
        print(f"[API] Stream completed. Total events sent: {event_count}")
        print("="*80)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    # Run FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
