import logging
import os
from datetime import datetime
from pathlib import Path

LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
LOG_DIR_PATH = os.path.join(Path(__file__).parent.parent, "logs")
os.makedirs(LOG_DIR_PATH, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR_PATH, LOG_FILE)

logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO, 
)

The above code can cause roadblock; it won't redirect logs to your file if another library initializes logging first. Because langchain and other third-party dependencies often configure basic logging internally at startup, your basicConfig call will be silently ignored, and your logs will keep dumping into the terminal console instead of writing to your logs/ directory.

Current code in logger_config works
Overwrites Hidden Handlers: Explicitly clearing root_logger.handlers breaks through third-party initializations, forcing everything in your pipeline (including Tavily client requests and LangChain tool errors) into your local log folder.
LOG_DIR_PATH.mkdir(parents=True, exist_ok=True) #parent=True to create intermediate directories if they don't exist why exist_ok=True to avoid error if the directory already exists both parent and exist_ok works same then why both are used together? parent=True is used to create intermediate directories if they don't exist, while exist_ok=True is used to avoid raising an error if the directory already exists. Using both together ensures that the necessary directory structure is created without causing issues if it already exists.

**##########################################################################**
def build_search_agent():
    global search_agent
    tools = [web_search, scape_url]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful research assistant that can perform web searches to assist with research tasks."),
            ("human", "{input}")  # The {input} variable will be replaced with the actual query or task when the agent is invoked. build_search_agent().invoke({"input": "What is the capital of France?"})
        ]
    )
    search_agent = create_agent(
        llm=llm,
        tools=[web_search],
        prompt=prompt,
        output_parser=StrOutputParser(),
        verbose=True
    )

If you notice your agent prints a response but never actually triggers your web_search or scrape_url functions, it is because a standard LLM combined with a StrOutputParser treats tools as plain text descriptions. It doesn't know how to stop, call the API, and read the results.

from langchain.agents import create_openai_tools_agent, AgentExecutor

def build_search_agent():
    agent_tools = [web_search, scrape_url]
 
    # Tool agents require an explicit placeholder for the chat/scratchpad notes
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful research assistant that can perform web searches to assist with research tasks."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}") 
    ])
    
    # 1. Create the base agent that binds your tools to your specific LLM
    agent = create_openai_tools_agent(llm=llm, tools=agent_tools, prompt=prompt)
    
    # 2. Wrap it inside an Executor to manage the API invocation loops automatically
    executor = AgentExecutor(agent=agent, tools=agent_tools, verbose=True)
    
    return executor


An LLM (Large Language Model) is just a text predictor. By default, it doesn't know how to run Python code or talk to the internet. It can only talk.

When you want an LLM to use a tool like your web_search, the process requires a loop that looks like this:

Human says: "What is the capital of France?"

LLM thinks: I need to use the web_search tool. 3. LLM outputs a special code instead of an answer: CALL TOOL: web_search("capital of France")

LangChain intercepts this text, runs your actual Python function, gets the results ("Paris"), and feeds them back to the LLM.

LLM looks at the results and finally says: "The capital of France is Paris."

**Why StrOutputParser breaks this loop**
When you attach output_parser=StrOutputParser(), you are telling LangChain: "Whatever the LLM outputs first, immediately turn it into a plain string and hand it back to me. We are done."

Because of that:

At Step 3, the LLM says: "I need to use the web_search tool..."

Instead of letting LangChain intercept that thought, run your Python function, and fetch the results, your StrOutputParser immediately grabs that raw thought text, stops the entire program, and returns it to you as the final answer.

Your web_search function is completely skipped because the chain stops before LangChain ever gets a chance to look at the tools.

**StrOutputParser() breaks the loop and returns first LLM answer so we shouldnt use it while using tools**
**##########################################################################**
When to use "search_result['messages'][-1].content"
You are actually 100% correct about search_result['messages'][-1].content—if you are using LangChain’s new standard create_agent module (introduced in the recent v1.0 updates).

Under the hood, the new create_agent compiles into a stateful graph that stores its execution history as a list of state messages rather than returning a legacy AgentExecutor dictionary.

However, because your ChatPromptTemplate is structured using input variables, the way you invoke it will cause the framework to crash. Here is exactly why your line is correct, but the code right above it needs a small adjustment to prevent a failure.

You use .get('output') when your agent is wrapped in the legacy AgentExecutor. This is the most common way agents were built until very recently.
Structure: The agent returns a standard Python dictionary.
# Example for AgentExecutor
result = agent_executor.invoke({"input": "query"})
print(result.get("output"))

You use .content when your agent is built as a LangGraph or uses the modern Stateful Graph approach (which is what your current create_agent setup likely produces).
# Example for Stateful Graphs / LangGraph
result = search_agent.invoke({"input": "query"})
# result['messages'] is a list of message objects
print(result['messages'][-1].content)
**##########################################################################**
Difference between LECL chain vs Agents

1. LCEL Chains are "One-Shot" (Static)Your writer_chain has a single, unchanging job: take some text, fill in the blanks, and give you a response.It follows a strict, predictable path: Input Text -> Prompt Template -> LLM -> Output Text.Because the flow never changes, it needs a ChatPromptTemplate to explicitly map your variables (like {topic} and {research}) into specific slots in the text.

2. An agent doesn't just process text in a straight line; it runs a loop where it decides on the fly what to do.Its path is completely unpredictable: Input -> Think -> Call Web Search Tool -> Get Results -> Think -> Call Scraper Tool -> Get Results -> Final Answer.Because it loops back and forth, the prompt isn't static. It grows dynamically as the agent adds its own "thoughts", tool requests, and tool answers to the message history.If you forced a static ChatPromptTemplate onto the agent, it would break the moment the agent tried to loop or inject a tool result, because there would be no pre-defined slot to hold that unpredictable conversational data.
**##########################################################################**
Types of Messages
1. System Message
2. Human Message
**##########################################################################**
**Langchain agents are sequential A->B->C But when we use langgraph we can loop like from A we go to B but if something fails we can loop back to A**


#DEPLOY IN RENDER.COM
#https://www.youtube.com/watch?v=9bGYJ68qvAA REFER THIS VIDEO'S LAST 10 MIN FOR DEPLOYMENT