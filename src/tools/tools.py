from langchain.tools import tool
import requests 
from dotenv import load_dotenv
import os
from tavily import TavilyClient
import logging
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re

logger = logging.getLogger(__name__)

def load_secretKeys_tools():
    load_dotenv()
    global TAVILY_API_KEY 
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def initialise_tavily_client():
    global tavily_client
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

@tool("web_search", return_direct=True)
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
            f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content'][:300]}\n"
        )
    logging.info(f"Formatted search results for query: '{query}'")
    logging.debug(f"Formatted search results: {output}")
    return "\n---\n".join(output)


@tool("scape_url", return_direct=True) # use tool.invoke to call this function in langchain agent
def scrape_url(url:str)-> str:
    """
    Scrapes the content of a given URL and returns the text.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status() # Check if the request was successful
        logging.info(f"Successfully fetched content from URL: {url}")

        html_content = response.text

        # Use trafilatura to extract the main content of the page
        extracted_content = trafilatura.extract(html_content, include_comments=False, include_tables=False)
        logging.info(f"Extracted content from URL: {url} with length: {len(extracted_content) if extracted_content else 0}")

        if extracted_content and len(extracted_content.strip()) > 200:
            cleaned_content = re.sub(r'\s+', ' ', extracted_content) #re.sub to replace multiple whitespace characters with a single space
            #eg: re.sub(r'\s+', ' ', "This   is   a   test.") will return "This is a test." \s+  matches one or more whitespace characters (spaces, tabs, newlines) and replaces them with a single space. This is useful for cleaning up text that may have irregular spacing.
            return cleaned_content[:5000]
        
        #readability is a fallback if trafilatura fails to extract meaningful content
        doc = Document(html_content)
        summary = doc.summary()

        soup = BeautifulSoup(summary, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()  # Remove script and style elements
        text = soup.get_text(separator="", strip=True)
        if text and len(text.strip()) > 200:
            cleaned_text = re.sub(r'\s+', ' ', text)
            logging.info(f"Extracted content from URL: {url} with length: {len(cleaned_text)}")
            return cleaned_text[:5000]
        
        # Fallback to returning the raw HTML if both methods fail to extract meaningful content
        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()  # Remove script and style elements
        raw_text = soup.get_text(separator="", strip=True)
        cleaned_raw_text = re.sub(r'\s+', ' ', raw_text)
        if cleaned_raw_text:
            return cleaned_raw_text[:5000]
        
        return "No meaningful content could be extracted from the URL."
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching content from URL: {url} - {e}")
        return f"Error fetching content from URL: {url} - {e}"
    except Exception as e:
        logging.error(f"Unexpected error while scraping URL: {url} - {e}")
        return f"Unexpected error while scraping URL: {url} - {e}"
    