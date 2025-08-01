"""
UI package for ShaheenAI
========================

This package contains user interface implementations for ShaheenAI,
including Streamlit and Chainlit integrations.
"""

# Optional imports with graceful fallback
try:
    from .streamlit_ui import StreamlitUI
except ImportError:
    StreamlitUI = None

try:
    from .chainlit_ui import ChainlitUI  
except ImportError:
    ChainlitUI = None

__all__ = [
    "StreamlitUI",
    "ChainlitUI",
]
