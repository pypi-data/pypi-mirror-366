"""
Streamlit UI for ShaheenAI
==========================

This module provides a Streamlit-based user interface for interacting
with ShaheenAI agents.
"""

import logging
import streamlit as st
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class StreamlitUI:
    """
    Streamlit UI for interacting with ShaheenAI agents.
    """
    
    def __init__(self, agent, title: str = "ShaheenAI Streamlit UI"):
        """
        Initialize the Streamlit UI with a given agent.

        Args:
            agent: The agent instance to interact with
            title: Title for the Streamlit UI app
        """
        self.agent = agent
        self.title = title

    def run(self):
        """
        Run the Streamlit application.
        """
        st.title(self.title)
        st.write("Interact with your AI agents through this Streamlit interface.")

        prompt = st.text_area("Enter your command:")

        if st.button("Submit"):
            self.process_command(prompt)

    def process_command(self, prompt: str):
        """
        Process a command through the agent and display the result.

        Args:
            prompt: The command prompt to process
        """
        st.write(f"Processing command: {prompt}")
        response = self.agent.start(prompt)
        st.write(f"Response: {response}")

