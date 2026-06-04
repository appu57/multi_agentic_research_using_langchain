import logging
import custom_logger.logger_config
from src.tools.tools import web_search, load_secretKeys, initialise_tavily_client

logger = logging.getLogger(__name__)

load_secretKeys()
initialise_tavily_client()
web_search_result = web_search("What is the capital of France?")
logger.info(f"Web search result: {web_search_result}")