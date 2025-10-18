from core.workflow import TrialWorkflow
from agents import LawyerAgent, ProsecutorAgent, JudgeAgent, RetrieverAgent, FetchingAgent, WebSearcherAgent
import asyncio
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
import os
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
import json

# Initialize FastAPI app
app = FastAPI()

# Initialize Ollama LLMs (Windows-compatible, free, local)
# Using ChatOllama for chat-based interactions
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Primary LLM for general use
llm_0 = ChatOllama(
    model=os.getenv("OLLAMA_MODEL_MAIN", "llama3.1:8b"),
    base_url=ollama_base_url,
    temperature=0.7
)

# Multiple LLM options for fallback redundancy
llms = [
    ChatOllama(
        model=os.getenv("OLLAMA_MODEL_MAIN", "llama3.1:8b"),
        base_url=ollama_base_url,
        temperature=0.7
    ),
    ChatOllama(
        model=os.getenv("OLLAMA_MODEL_ADVANCED", "mistral:7b"),
        base_url=ollama_base_url,
        temperature=0.7
    ),
    ChatOllama(
        model="llama3.1:8b",
        base_url=ollama_base_url,
        temperature=0.8
    ),
]

print("="*80)
print("OLLAMA LLM INITIALIZATION")
print("="*80)
print(f"Ollama Base URL: {ollama_base_url}")
print(f"Primary Model: {os.getenv('OLLAMA_MODEL_MAIN', 'llama3.1:8b')}")
print(f"Advanced Model: {os.getenv('OLLAMA_MODEL_ADVANCED', 'mistral:7b')}")
print("Primary LLM initialized successfully")
print(f"Fallback LLM count: {len(llms)}")
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
