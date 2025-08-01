# shaheenai

ShaheenAI is a flexible, multi-LLM, agent-oriented Python library that supports multiple language model providers like OpenAI, Anthropic, Ollama, and Cohere via a plugin/extras architecture. The library offers self-reflection, tool invocation, task chaining, and optional UI integrations using Streamlit and Chainlit.

## Features
- **Modular Agent Class:** Supports multiple LLMs with self-reflection, tool invocation, and task chaining.
- **MCP Server Interface:** Optionally integrates tools and external APIs.
- **Configurable via YAML or Code:** Supports playbooks and programmatic configuration.
- **Wide LLM Provider Support:** OpenAI, Anthropic, Ollama, Cohere, etc.
- **Streamlit and Chainlit Support:** Build interactive and conversational UIs for agents.

## Getting Started

### Prerequisites
- Python 3.10 or higher

### Installation
To install ShaheenAI, use pip:
```bash
pip install shaheenai
```

### Usage
Here's a basic example of how to use ShaheenAI to create an agent that utilizes a weather tool:

```python
from shaheenai.agent import Agent
from shaheenai.mcp import MCP

# Define and run the MCP server
mcp = MCP()
@mcp.tool()
async def get_weather(location: str) -> str:
    return "Sunny with 25°C"

if __name__ == "__main__":
    mcp.run()

# Create an agent
agent = Agent(instructions="You can use tools when needed", llm="openai", tools=["get_weather"])
response = agent.start("What's the weather in Lahore today?")
print(response)
```

### CLI
ShaheenAI provides a command-line interface for running agents defined in YAML playbooks or via auto-mode.

Example:
```bash
shaheenai run agents.yaml
```

## Directory Structure
```
shaheenai/
 ├── shaheenai/
 │    ├── __init__.py
 │    ├── agent.py
 │    ├── mcp.py
 │    ├── llm_providers/
 │    │     ├── openai.py
 │    │     ├── cohere.py
 │    │     └── ...
 │    ├── tools/
 │    └── config.py
 ├── setup.py or pyproject.toml
 ├── README.md
 ├── LICENSE  # e.g. MIT
 └── examples/
      ├── app.py
      └── agents.yaml
```

## Contributing
Contributions are welcome! Please read the contribution guidelines first.

## License
This project is licensed under the MIT License.

## Acknowledgments
Inspired by PraisonAI for its modularity and multi-LLM support.
