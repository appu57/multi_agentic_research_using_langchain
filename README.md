# ResearcherAgent: Multi-Agent AI System

ResearcherAgent is a sophisticated multi-agent AI system built with **LangChain** and **Streamlit**. It coordinates four specialized AI entities—searching, scraping, writing, and critiquing—to deliver polished, deep-dive research reports on any topic in minutes.

---

## 🤖 The Multi-Agent Pipeline

The system utilizes a sequential pipeline where each agent builds upon the work of the previous one:

1.  **Search Agent**: Leverages search tools to gather the most recent and relevant information from across the web.
2.  **Reader Agent**: Performs deep content extraction by scraping identified high-value URLs to move beyond surface-level search snippets.
3.  **Writer Chain**: Synthesizes gathered data into a structured, professional research report including introductions, key findings, and source citations.
4.  **Critic Chain**: Conducts a final review of the report, providing a score and specific feedback on strengths and areas for improvement.

---

## ✨ Features

* **Real-time Progress Tracking**: A dynamic "Pipeline" UI panel shows the live state of each agent (Waiting, Running, or Done).
* **Deep Scraping**: Unlike simple search bots, this system extracts full text from websites to ensure high-density information.
* **Professional Formatting**: Outputs reports in clean Markdown with logical sections and a formal tone.
* **Quality Control**: Every report is automatically critiqued by an AI "Critic" to ensure accuracy and depth.
* **One-Click Export**: Download your final research report as a `.txt` or `.md` file instantly.

---

## 🛠️ Technology Stack

* **Framework**: [LangChain](https://www.langchain.com/) for agent orchestration and LCEL (LangChain Expression Language) chains.
* **LLMs**: Powered by high-speed Groq inference (`llama-3.3-70b-versatile`).
* **Frontend**: [Streamlit](https://streamlit.io/) with custom CSS for a modern, dark-themed research interface.
* **Search Engine**: Integrated with Tavily for AI-optimized web search results.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* API Keys for **Groq** and **Tavily**

### Installation
1. Clone or navigate to the repository directory:
   ```bash
   cd C:\Users\apoor\Projects\multi_agentic_research_using_langchain