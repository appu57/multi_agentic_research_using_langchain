from langchain.tools import tool
import requests 
from dotenv import load_dotenv
import os
from tavily import TavilyClient
import logging

logger = logging.getLogger(__name__)

def load_secretKeys():
    load_dotenv()
    global OPENAI_API_KEY, TAVILY_API_KEY 
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def initialise_tavily_client():
    global tavily_client
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

def web_search(query:str) -> str:
    """
    Performs a web search using the Bing Search API and returns the results as a string.
    """
    requests = tavily_client.search(query=query, num_results=5)
    logging.info(f"Web search performed for query: '{query}' with {len(requests)} results.")
    logging.debug(f"Search results: {requests}")
    output = []
    for r in requests['results']:
        output.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )
    logging.info(f"Formatted search results for query: '{query}'")
    logging.debug(f"Formatted search results: {output}")
    return "\n".join(output)
