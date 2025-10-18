import json
import os
import requests
from crewai.tools import tool
from duckduckgo_search import DDGS

class SearchTools():
    @staticmethod
    def get_serper_search_results(queries: list, top_result_to_return: int = 4) -> list:
        """
        Perform a search using Serper API.
        
        Args:
            queries (list): Search terms to query.
            top_result_to_return (int): Number of top results to return.
        
        Returns:
            str: Formatted search results or error message.
        """
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': os.environ.get('SERPER_API_KEY', ''),
            'content-type': 'application/json'
        }
        string = []

        for query in queries:
            try:
                payload = json.dumps({"q": query})
                response = requests.request("POST", url, headers=headers, data=payload)
                
                # Check if API key is invalid or request failed
                if response.status_code != 200 or 'organic' not in response.json():
                    raise Exception("Serper API request failed")
                
                results = response.json()['organic']
                for result in results[:top_result_to_return]:
                    try:
                        string.append('\n'.join([
                            f"Title: {result['title']}", f"Link: {result['link']}",
                            f"Snippet: {result['snippet']}", "\n-----------------"
                        ]))
                    except KeyError:
                        continue
            
            except Exception as e:
                # If Serper fails, log the error and move to Bing search
                print(f"Serper search failed for query '{query}': {str(e)}")
                return SearchTools.get_duckduckgo_search_results(queries)
        
        return '\n'.join(string)

    @staticmethod
    def get_duckduckgo_search_results(queries: list, top_result_to_return: int = 4) -> str:
        """
        Perform a search using DuckDuckGo search API.
        
        Args:
            queries (list): Search terms to query.
            top_result_to_return (int): Number of top results to return.
        
        Returns:
            str: Formatted search results.
        """
        string = []

        for query in queries:
            try:
                # Perform DuckDuckGo search
                with DDGS() as ddgs:
                    results = list(ddgs.text(
                        query, 
                        region='in-in', 
                        max_results=top_result_to_return
                    ))
                
                for result in results:
                    try:
                        string.append('\n'.join([
                            f"Title: {result['title']}", 
                            f"Link: {result['href']}", 
                            f"Snippet: {result['body']}", 
                            "\n-----------------"
                        ]))

                    except KeyError:
                        continue
            
            except Exception as e:
                # If DuckDuckGo search fails
                print(f"DuckDuckGo search failed for query '{query}': {str(e)}")
                string.append(f"Search failed for query: {query}")
        
        return '\n'.join(string)

    @tool("Search the internet")
    def search_internet(queries: list) -> str:
        """
        Perform an internet search using the provided queries.

        This method searches the internet and returns
        the top search results as a formatted string.
        
        Args:
            queries (list): Search terms to query.
        
        Returns:
            str: Formatted search results with title,link and summary.
        """
        # First try Serper search
        return SearchTools.get_serper_search_results(queries)