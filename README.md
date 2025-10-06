# {{crew_name}} Crew

Welcome to the {{crew_name}} Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```

### Customizing

**Add your `OPENAI_API_KEY` or any API provider of your choice into the `.env` file**

**Configure your Provider according to the documentation: [LLMs](https://docs.crewai.com/en/concepts/llms)**

- Set the LLM inside `src/test2/research_flow.py` in the __init__-Block
```python
from crewai import LLM

llm = LLM(model="gpt-4")

def __init__(self):
        super().__init__()
        self.llm = llm
```
- Set your embedding model inside `src/test2/research_flow.py` in the Chroma-Configuration
```python
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

For example with Ollama:

ollama_embeddings = OllamaEmbeddings(model="nomic-embed-text")

self.vector_store = Chroma(
            collection_name="collection",
            embedding_function=ollama_embeddings,
            ...
        )
```
- Modify `src/test2/research_flow.py` to if you want to change agents or task

## Running the Project

** Start the MCP-Server
```bash
uv run python ./src/test2/mcp_server.py
```

** Start the MCP-Client in another terminal
```bash
uv run python ./src/test2/mcp_client.py
```

Enter a topic and wait
