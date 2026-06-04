import logging
import custom_logger.logger_config
from src.pipeline.pipeline import run_research_pipeline
logger = logging.getLogger(__name__)

topic = "The impact of AI on the job market in 2026"
results= run_research_pipeline(topic)
logger.info(f"Web search result: {results}")