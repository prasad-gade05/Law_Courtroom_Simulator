import os
import time
from typing import Dict, Any, List, Optional
from .base import AgentState
from .misc.filestorage import FileStorage
from .misc.ik import IKApi
import argparse
import json
import shutil
from dotenv import load_dotenv

# Class to handle keyword extraction from legal documents
class KeywordExtractorAgent:
    def __init__(self,
        documents: List[Any],
        llms
    ):
        self.documents = documents
        self.llms = llms

        # Define the system prompt for the task
        self.system_prompt = {
            "role": "system",
            "content": """You are an assistant that helps users extract relevant keywords from legal documents for their legal case. Your tasks are:

            1. Understand the user's legal case based on the provided description.
            2. Analyze the provided documents related to the case.
            3. Identify and extract only 5 most relevant keywords, phrases, and legal terms that are most relevant to the user's case.
            4. Provide the user with a list of these keywords to help them search for supportive cases and information on law websites.
            5. Ensure that the keywords are specific, relevant, and cover all aspects of the user's case.

            Guidelines:

            - Focus on legal terms, case identifiers, statutory references, key legal concepts, and any unique aspects of the case.
            - Consider synonyms and related terms that might be used in legal databases.
            - Do not include irrelevant information or overly general terms.
            - Give only top 5 most relevant keywords.
            """
        }
    async def extract_keywords(self, user_case: str) -> Dict[str, Any]:
        """Extract relevant keywords based on the user's case and documents."""
        documents_content = "\n".join([doc for doc in self.documents])
        # print("case files from user:",documents_content)
        prompt = f"""User Case Description:
{user_case}

Relevant Documents:
{documents_content}

Based on the above user case and documents, extract a list of relevant keywords, phrases, and legal terms that the user can use to search for supportive cases and information. The keywords should be specific to the user's case and cover all important aspects.

Provide the list of keywords in bullet point format.
"""
        response = self._get_llm_response(prompt)
        keywords = self._parse_keywords(response)
        return keywords

    def _get_llm_response(self, prompt: str) -> str:
        """Get response from the LLM."""
        # response = self.llm.invoke([
        #     {"role": "system", "content": self.system_prompt['content']},
        #     {"role": "user", "content": prompt}
        # ])
        for i,llm in enumerate(self.llms):
            try:
                response = llm.invoke([
                    {"role": "system", "content": self.system_prompt['content']},
                    {"role": "user", "content": prompt}
                ])
                break
            except Exception as e:
                print(f"LLM {i} failed with error: {e}")
                continue
        return response.content

    def _parse_keywords(self, response: str) -> Dict[str, Any]:
        """Parse the response to extract keywords."""
        lines = response.strip().split("\n")
        keywords = [
            line.strip("- ").strip() 
            for line in lines
            if line.strip()
        ]
        # Return the keywords only once in the correct structure
        return {"type": "keywords", "keywords": keywords}


load_dotenv()


class Document:
    def __init__(self, content: str):
        self.content = content

class FetchingAgent:
    """Agent responsible for fetching relevant docs from the kanoon api"""
    
    def __init__(self, llms):
        self.llms = llms
        print("initialised kanoon fetcher...")
        # super().__init__(**kwargs)

    
    async def process(self, state: AgentState) -> AgentState:
        """Process current state with fetching-specific logic"""
        kanoon_api_key = os.getenv("KANOON_API_KEY")
        if not kanoon_api_key:
            raise ValueError("KANOON_API_KEY not found in environment variables.")

        data_directory = "public_documents"
        os.makedirs(data_directory, exist_ok=True)
        filestorage = FileStorage(data_directory)

        args = argparse.Namespace(
            token=kanoon_api_key,
            datadir=data_directory,
            maxpages=2,  # Limit number of pages
            maxcites=0,
            maxcitedby=0,
            orig=False,
            pathbysrc=True
        )

        # Initialize Indian Kanoon API client
        ikapi = IKApi(args, filestorage)

        # List to store the content of the text files uploaded by user
        folder_path = 'private_documents'
        documents = []

        # Loop through all files in the folder
        for filename in os.listdir(folder_path):
            # Check if the file is a text file
            if filename.endswith('.txt'):
                file_path = os.path.join(folder_path, filename)
                
                # Read the file content
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    documents.append(content)

        # Extract Keywords
        agent = KeywordExtractorAgent(documents=documents, llms=self.llms)
        keywords_result = await agent.extract_keywords(user_case=state["messages"][-1].content)  # Await the coroutine

        # Step 2: Use Extracted Keywords for Searching Relevant Cases
        print("Extracted Keywords:")
        keywords = keywords_result["keywords"]
        for keyword in keywords:
            print(f"- {keyword}")

        # Specify max_docs per keyword (reduced for faster demo)
        MAX_DOCS_PER_KEYWORD = 1  # Reduced from 2 to 1 for faster execution
        MAX_KEYWORDS = 3  # Reduced from 5 to 3

        all_doc_ids = []
        for idx, keyword in enumerate(keywords[:MAX_KEYWORDS], 1):
            print(f"[{idx}/{MAX_KEYWORDS}] Searching for keyword: {keyword[:80]}...")  # Truncate for display
            try:
                doc_ids = ikapi.save_search_results(keyword, max_docs=MAX_DOCS_PER_KEYWORD)
                all_doc_ids.extend(doc_ids)
                print(f"    Found {len(doc_ids)} documents")
            except Exception as e:
                print(f"    Error fetching: {e}")
                continue
            
        # Print the total number of documents fetched
        print(f"✓ Total documents fetched: {len(all_doc_ids)}")

        # converting fetched json data from the API to texts, not doing it 
        # Path to the 'public' directory
        # base_path = "public_documents"

        # # Loop through all unique subfolders, created by the storage utility, in the base directory
        # for unique_folder in os.listdir(base_path):
        #     unique_folder_path = os.path.join(base_path, unique_folder)
            
        #     # Skip if not a folder
        #     if not os.path.isdir(unique_folder_path):
        #         continue
            
        #     # Text content to combine for the current unique folder
        #     combined_text = []
            
        #     # Traverse the hierarchy within the unique folder
        #     for court_folder in os.listdir(unique_folder_path):
        #         court_folder_path = os.path.join(unique_folder_path, court_folder)
                
        #         if not os.path.isdir(court_folder_path):
        #             continue
                
        #         for year_folder in os.listdir(court_folder_path):
        #             year_folder_path = os.path.join(court_folder_path, year_folder)
                    
        #             if not os.path.isdir(year_folder_path):
        #                 continue
                    
        #             for date_folder in os.listdir(year_folder_path):
        #                 date_folder_path = os.path.join(year_folder_path, date_folder)
                        
        #                 if not os.path.isdir(date_folder_path):
        #                     continue
                        
        #                 # Process each JSON file in the date folder
        #                 for file_name in os.listdir(date_folder_path):
        #                     file_path = os.path.join(date_folder_path, file_name)
                            
        #                     # Skip if not a JSON file
        #                     if not file_name.endswith(".json"):
        #                         continue
                            
        #                     try:
        #                         # Load and extract JSON content
        #                         with open(file_path, "r", encoding="utf-8") as json_file:
        #                             data = json.load(json_file)
                                    
        #                             # Convert JSON content to string and append to combined_text
        #                             combined_text.append(json.dumps(data, indent=4))
        #                     except Exception as e:
        #                         print(f"Error processing file {file_path}: {e}")
            
        #     # Write the combined text to a single file named after the unique folder
        #     if combined_text:
        #         output_file_path = os.path.join(base_path, f"{unique_folder}.txt")
        #         with open(output_file_path, "w", encoding="utf-8") as output_file:
        #             output_file.write("\n\n".join(combined_text))
        #         print(f"Created combined text file: {output_file_path}")

        #         # Delete the unique folder after successful processing
        #         try:
        #             shutil.rmtree(unique_folder_path)
        #             print(f"Deleted folder: {unique_folder_path}")
        #         except Exception as e:
        #             print(f"Error deleting folder {unique_folder_path}: {e}")

        # time.sleep(10)
        
        # Return state to continue workflow
        from langchain_core.messages import HumanMessage
        
        response = {
            "messages": [HumanMessage(content=f"Fetched {len(all_doc_ids)} relevant legal cases from Kanoon API based on extracted keywords.", name="kanoon_fetcher")],
            "next": "prosecutor",
            "thought_step": 0,
            "caller": "kanoon_fetcher"
        }
        
        return response
