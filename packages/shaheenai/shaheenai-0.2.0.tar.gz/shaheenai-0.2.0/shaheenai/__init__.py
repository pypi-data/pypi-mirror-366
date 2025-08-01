"""
ShaheenAI - A flexible, multi-LLM, agent-oriented Python library
================================================================

ShaheenAI provides a modular framework for building AI agents with support for
multiple language model providers, self-reflection capabilities, tool integration,
and UI frameworks like Streamlit and Chainlit.

Key Features:
- Multi-LLM support (OpenAI, Anthropic, Ollama, Cohere, etc.)
- Agent-based architecture with self-reflection
- MCP (Model Context Protocol) server for tool integration
- YAML and code-based configuration
- Streamlit and Chainlit UI integrations

Author: Hamza
License: MIT
"""

__version__ = "0.2.0"
__author__ = "Hamza - AI Engineer, Python Developer, Machine Learning, Agentic AI, Data Science, Node, Express, Typescript, NextJS"

from .agent import Agent
from .config import Config
from .mcp import MCP, tool

# Research module imports
try:
    from .research import ResearchPlanner, BibliographyManager, ResearchProject, ResearchTemplates
except ImportError:
    ResearchPlanner = None
    BibliographyManager = None 
    ResearchProject = None
    ResearchTemplates = None

# Optional imports with graceful fallback
try:
    from .ui.streamlit_ui import StreamlitUI
except ImportError:
    StreamlitUI = None

try:
    from .ui.chainlit_ui import ChainlitUI
except ImportError:
    ChainlitUI = None

__all__ = [
    "Agent",
    "Config", 
    "MCP",
    "tool",
    "StreamlitUI",
    "ChainlitUI",
    "ResearchPlanner",
    "BibliographyManager",
    "ResearchProject",
    "ResearchTemplates",
]
