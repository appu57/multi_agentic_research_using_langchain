from langchain.agents import create_agent #create_react_agent is deprecated
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser # StrOutputParser is a simple output parser that just returns the string output from the model, without any additional parsing or formatting. This can be useful when you want to get the raw response from the model without any modifications.
from src.tools.tools import web_search, scrape_url
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
import logging

logger = logging.getLogger(__name__)
GROQ_API_KEY = None
llm = None
writer_chain = None
critic_chain = None
def load_secretKeys_agents():
    load_dotenv()
    global GROQ_API_KEY 
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def initialize_llm():
    global llm, GROQ_API_KEY
    if GROQ_API_KEY is None:
        load_secretKeys_agents()
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.0, #0.7 introduces creative variance, which increases the likelihood of formatting errors. For structured agents relying on tool calling, the temperature should ideally be scaled down close to 0 to keep the syntax generation predictable and compliant with Groq's formatting engine.
        api_key=GROQ_API_KEY
    )

def build_search_agent():
    global search_agent
    # Removed the ChatPromptTemplate wrapper which is incompatible with create_agent.
    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         ("system", "You are a helpful research assistant that can perform web searches to assist with research tasks."),
    #         ("human", "{input}")  # The {input} variable will be replaced with the actual query or task when the agent is invoked. build_search_agent().invoke({"input": "What is the capital of France?"})
    #     ]
    # )
    search_agent = create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=(
            "You are a precise research assistant. When you need to search, "
            "invoke your tool call strictly using valid JSON formatting. Do not wrap your "
            "tool requests in text, codeblocks, markdown tags, or custom tags like <function>."
        )
    )
    return search_agent

def use_scraper_agent():
    global scraper_agent
    scraper_agent = create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt=(
            "You are a structural content scraper. When parsing URLs, "
            "format your tool inputs strictly as clear JSON objects without any wrapper tags."
        )
    )
    return scraper_agent


def initialize_chains():
    writer_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
        ("human", """Write a detailed research report on the topic below.

    Topic: {topic}

    Research Gathered:
    {research}

    Structure the report as:
    - Introduction
    - Key Findings (minimum 3 well-explained points)
    - Conclusion
    - Sources (list all URLs found in the research)

    Be detailed, factual and professional."""),
    ])

    writer_chain = writer_prompt | llm | StrOutputParser()



    critic_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a sharp and constructive research critic. Be honest and specific."),
        ("human", """Review the research report below and evaluate it strictly.

    Report:
    {report}

    Respond in this exact format:

    Score: X/10

    Strengths:
    - ...
    - ...

    Areas to Improve:
    - ...
    - ...

    One line verdict:
    ..."""),
    ])

    critic_chain = critic_prompt | llm | StrOutputParser()
    return writer_chain, critic_chain

# We now don't use chatPromptTemplate for the agents, instead we directly create agents using create_agent and pass the tools. The prompts are now only used for the writer and critic chains, which are separate from the search and scraper agents. This allows us to have more flexibility in how we structure the interactions with the agents and use the tools effectively.
# def create_agent(
#     model: str | BaseChatModel,
#     tools: Sequence[BaseTool | Callable[..., Any] | dict[str, Any]] | None = None,
#     *,
#     system_prompt: str | SystemMessage | None = None,  
#     middleware: Sequence[AgentMiddleware[StateT_co, ContextT]] = (),
#     response_format: ResponseFormat[ResponseT] | type[ResponseT] | dict[str, Any] | None = None,
#     state_schema: type[AgentState[ResponseT]] | None = None,
#     context_schema: type[ContextT] | None = None,
#     checkpointer: Checkpointer | None = None,
#     store: BaseStore | None = None,
#     interrupt_before: list[str] | None = None,
#     interrupt_after: list[str] | None = None,
#     debug: bool = False,
#     name: str | None = None,
#     cache: BaseCache[Any] | None = None,
#     transformers: Sequence[TransformerFactory] | None = None,
# ) -> CompiledStateGraph[
#     AgentState[ResponseT], ContextT, _InputAgentState, _OutputAgentState[ResponseT]
# ]: