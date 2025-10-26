from core.workflow import TrialWorkflow
from agents import LawyerAgent, ProsecutorAgent, JudgeAgent, RetrieverAgent, FetchingAgent, WebSearcherAgent
import asyncio
from langchain_ollama import OllamaLLM
import os
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize Ollama LLM
ollama_model = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")

print("="*80)
print("OLLAMA LLM INITIALIZATION")
print("="*80)
print(f"Model: {ollama_model}")
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
print(f"Base URL: {base_url}")
print("="*80)

# Primary LLM for all agents
try:
    llm = OllamaLLM(model=ollama_model, stop=["\nObservation:"])
    # Perform a quick test to ensure Ollama server is running
    llm.invoke("test") 
    print("Primary LLM initialized and connected to Ollama successfully")
except Exception as e:
    print(f"ERROR: Failed to initialize or connect to Ollama: {e}")
    print("Please ensure Ollama is running and the model is pulled")
    raise

# Use the same LLM instance for all agents for consistency
llms = [llm, llm, llm]
llm_0 = llm

print(f"LLM instances created for all agents")
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
    llms=llms  # Add llms parameter for VerdictAgent
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