from typing import Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from core.chroma_store import ChromaVectorStore
from .base import AgentState
from langchain_core.messages.utils import get_buffer_string
import os
from dotenv import load_dotenv
load_dotenv()
import re


def create_law_retriever(private=False) -> BaseTool:
    """Create ChromaDB vector store retriever for legal documents"""
    vector_store = None
    if private:
        vector_store = ChromaVectorStore('private', './private_documents')
    else:
        vector_store = ChromaVectorStore('public', './public_documents')

    # Get retriever from vector store (compatible with old interface)
    retriever = vector_store.as_retriever()

    return retriever
   
# class RetrieverResponse(BaseModel):
#     """Structured retriever response"""
#     # response: str = Field(description="The retriever's assessment of the retrieved content")
#     is_enough: bool = Field(description="Whether the retrieved content is enough to answer the request")

# class Queries(BaseModel):
#     private_query: str = Field(description="Query for private retriever (user case files or documents). 'none' if not needed")  
#     public_query: str = Field(description="Query for public retriever (public docs like IPC, legal case precedents, etc) 'none' if not needed")
class RetrieverAgent:
    """Agent for retrieving and analyzing legal documents from vector store"""
    
    def __init__(
        self,
        llms,
        # **kwargs
    ):
        self.private_retriever = create_law_retriever(private=True)
        self.public_retriever = create_law_retriever(private=False)
        # self.llm = llm or ChatGroq(model="llama-3.1-70b-versatile", api_key=os.getenv('GROQ_API_KEY'))
        self.llms = llms
        self.system_prompt = """
"You are a legal research assistant specializing in retrieving relevant legal provisions, case laws, and statutes from a vector database of the Indian Penal Code (IPC) and related legal documents."
"Formulate queries based on inputs from the judge, lawyer, or prosecutor, ensuring precision in the retrieval process."
"Evaluate the retrieved text for relevance and clarity before sharing it with the requesting agent. If the retrieval is insufficient, refine the query and attempt again."
"you have acsess to private retrierver (contains user case files or documents) and public retriever (contains public docs like IPC, legal case precedents, etc)"
"Your role is critical in supporting the legal arguments by providing accurate and contextually appropriate legal references."
"Ensure that your outputs are succinct, relevant, and formatted for easy understanding by the requesting agent."

you will go through the following chain of thought steps:
1. Analyze the information request.
2. Form the queries.
3. Assess the retrieved results.
4. Provide accurate excerpts of information

IMPORTANT NOTE: Do only 'current_task' at a time, other task will be done in next steps or other agents. Avoid very long responses.
"""

    def get_thought_steps(self) -> List[str]:
        """Get retriever-specific chain of thought steps"""
        return [
            "1. Analyze the information request received from the lawyer or prosecutor and Note the key words and points.",
            "2. Accordiing to the resqusted information, if private_retriever(user case files or user documents) is needed, form a query for it. if not respond with only 'none'",
            "3. Accordiing to the resqusted information, if public_retriever(contains public docs like IPC, legal case precedents, etc) is needed, form a query for it. if not respond with only 'none'",
            "4. Assess the retrieved results and determine If they are relevent and enough. if yes, respond with keyword 'is_enough', if not respond with keyword 'not_enough'",
            "5. Provide the lawyer or prosecutor with accurate excerpts of relevant laws based on the request, ensuring clarity.If no relevant law is found, respond with 'No relevant law found in database.'"
        ]

    async def process(self, state: AgentState) -> AgentState:
        """Process current state with retriever-specific logic"""
        
        messages = [
            {"role": "system", "content": self.system_prompt + f"\n'current_task': {self.get_thought_steps()[0]}"}
        ] + state["messages"]

        # info_analysis = self.llm.invoke(messages)

        for i,llm in enumerate(self.llms):
            try:
                info_analysis = llm.invoke(messages)
                break
            except Exception as e:
                print(f"LLM {i} failed with error: {e}")
                continue

            
        for i in range(1): # max 5 iterations
            #formulate query
            messages.append({"role": "system", "content": "need_info: " + info_analysis.content + "\n" + "current_task: " + self.get_thought_steps()[1]})
            # queries = self.llm.with_structured_output(Queries).invoke(messages)
            for i,llm in enumerate(self.llms):
                try:
                    private_query = llm.invoke(messages)
                    public_query = llm.invoke(messages)
                    break
                except Exception as e:
                    print(f"LLM {i} failed with error: {e}")

            #retrieve
            private_retrieved_content = self.private_retriever.invoke(private_query.content) if private_query.content.lower() != 'none' else 'None'
            public_retrieved_content = self.public_retriever.invoke(public_query.content) if public_query.content.lower() != 'none' else 'None'

            #assess
            messages.append({"role": "system", "content": "private_retrieved_content: " + str(private_retrieved_content) + "\npublic_retrieved_content: " + str(public_retrieved_content) + "\ncurrent_task: " + self.get_thought_steps()[2]})
            # assessment = self.llm.with_structured_output(RetrieverResponse).invoke(messages)
            for i,llm in enumerate(self.llms):
                try:
                    assessment = llm.invoke(messages)
                    break
                except Exception as e:
                    print(f"LLM {i} failed with error: {e}")
                    continue

            #continue
            if not re.search(r"not_enough", assessment.content, re.IGNORECASE):
                break

                
            
        
        messages.append({"role": "system", "content": "private_retrieved_content: " + str(private_retrieved_content) + "\npublic_retrieved_content: " + str(public_retrieved_content) + "\ncurrent_task: " + self.get_thought_steps()[3]})
        # result = self.llm.invoke(messages)
        for i,llm in enumerate(self.llms):
            try:
                result = llm.invoke(messages)
                break
            except Exception as e:
                print(f"LLM {i} failed with error: {e}")
                continue

        
        
        response = {
            "messages": [HumanMessage(content=result.content, name="retriever")],
            "next": state["caller"],
            "thought_step": state["thought_step"],
            "caller": "retriever"
        }
   
            
        return response
    
                    
        