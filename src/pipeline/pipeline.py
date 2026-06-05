from src.agents.agents import load_secretKeys_agents, initialize_llm, build_search_agent, use_scraper_agent, initialize_chains
import logging
from src.tools.tools import web_search, load_secretKeys_tools, initialise_tavily_client

logger = logging.getLogger(__name__)

def run_research_pipeline(topic:str) -> dict:
    load_secretKeys_agents()
    load_secretKeys_tools()
    initialise_tavily_client()
    initialize_llm()

    state = {}

    logger.info(f"Starting research pipeline for topic: '{topic}'")
    
    search_agent =  build_search_agent()
    search_result = search_agent.invoke({
        "messages": [{"role": "user", "content": f"Find recent information about {topic}"}]
    })
    state['search_result'] = search_result['messages'][-1].content
    logger.info(f"Search results obtained for topic: '{topic}'")
    logger.debug(f"Search results: {state['search_result']}")
   

    logger.info(f"Starting content scraping for topic: '{topic}'")
    scaper_agent =  use_scraper_agent()
    scrapped_result = scaper_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_result'][:800]}"
        )]
        #why user (acts as a role) ? because the agent is designed to take in messages in a conversational format, where the user provides input and the agent responds. By structuring the input as a message from the user, we can effectively communicate the task to the agent and allow it to process the information accordingly.
    })
    state['scapped_content'] = scrapped_result['messages'][-1].content
    logger.info(f"Content scraping completed for topic: '{topic}'")
    logger.debug(f"Scrapped content: {state['scapped_content']}")



    logger.info(f"Starting report writing for topic: '{topic}'")
    research_combined = (
        f"Search Results:\n{state['search_result']}\n\n"
        f"Scrapped Content:\n{state['scapped_content']}"
    )

    writer_chain, critic_chain =  initialize_chains()

    state['report'] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })
    logger.info(f"Report writing completed for topic: '{topic}'")

    state['feedback'] = critic_chain.invoke({
        "report": state['report']   
    })
    logger.info(f"Report critique completed for topic: '{topic}'")
    return state