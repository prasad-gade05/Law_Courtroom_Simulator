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

print(f"✓ Initialized Ollama LLMs with base URL: {ollama_base_url}")
print(f"  Primary model: {os.getenv('OLLAMA_MODEL_MAIN', 'llama3.1:8b')}")
print(f"  Fallback models: {len(llms)} configured")

# Initialize Workflow
workflow = TrialWorkflow(
    lawyer=LawyerAgent(llms=llms),
    prosecutor=ProsecutorAgent(llms=llms),
    judge=JudgeAgent(llms=llms),
    retriever=RetrieverAgent(llms=llms),
    kanoon_fetcher=FetchingAgent(llms=llms),
    web_searcher=WebSearcherAgent(llm=llm_0),
)

# Visualization removed - graph not needed in production

@app.post("/stream_workflow")
async def stream_workflow(user_prompt: str = Body(..., embed=True)):
    async def event_generator():
        async for state in workflow.run(user_prompt=user_prompt):
            # # Ensure state is serialized properly
            # if isinstance(state["state"], str):
            #     # Parse string-like dictionaries back into JSON
            #     state["state"] = json.loads(state["state"].replace("'", '"'))  # Convert single quotes to double quotes if needed
            yield f"data: {json.dumps(state)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    # Run FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
