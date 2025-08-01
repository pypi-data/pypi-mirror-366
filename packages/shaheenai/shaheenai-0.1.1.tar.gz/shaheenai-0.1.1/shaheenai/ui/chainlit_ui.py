"""
Chainlit UI for ShaheenAI
=========================

This module provides a Chainlit-based chat interface for interacting
with ShaheenAI agents.
"""

import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)


class ChainlitUI:
    """
    Chainlit UI for interacting with ShaheenAI agents.
    
    This class provides a chat-based interface using Chainlit for
    real-time conversations with AI agents.
    """
    
    def __init__(self, agent, title: str = "ShaheenAI Chat"):
        """
        Initialize the Chainlit UI.
        
        Args:
            agent: The agent instance to interact with
            title: Title for the chat interface
        """
        self.agent = agent
        self.title = title
        self._chainlit_available = True
        
        try:
            import chainlit as cl
            self.cl = cl
        except ImportError:
            logger.error("Chainlit not available. Install with: pip install chainlit")
            self._chainlit_available = False
    
    def setup_handlers(self):
        """Setup Chainlit event handlers."""
        if not self._chainlit_available:
            return
        
        @self.cl.on_chat_start
        async def start():
            """Handler for when a chat session starts."""
            await self.cl.Message(
                content=f"Hello! I'm {self.title}. How can I help you today?"
            ).send()
        
        @self.cl.on_message
        async def main(message: self.cl.Message):
            """Handler for incoming messages."""
            try:
                # Send the message to the agent
                response = await self.agent.astart(message.content)
                
                # Send the response back
                await self.cl.Message(content=response).send()
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                await self.cl.Message(content=error_msg).send()
    
    def run(self):
        """
        Run the Chainlit application.
        
        Note: This method sets up the handlers. The actual running
        is done by the Chainlit CLI command.
        """
        if not self._chainlit_available:
            raise ImportError("Chainlit not available. Install with: pip install chainlit")
        
        self.setup_handlers()
        logger.info(f"Chainlit UI configured for {self.title}")


# Standalone Chainlit app that can be run directly
def create_chainlit_app(agent=None):
    """
    Create a standalone Chainlit app.
    
    Args:
        agent: Optional agent instance. If None, creates a default agent.
    """
    try:
        import chainlit as cl
        from ..agent import Agent
        
        # Create default agent if none provided
        if agent is None:
            agent = Agent(
                instructions="You are a helpful AI assistant.",
                llm="openai/gpt-3.5-turbo",
                memory=True
            )
        
        @cl.on_chat_start
        async def start():
            """Handler for when a chat session starts."""
            await cl.Message(
                content="Hello! I'm ShaheenAI. How can I help you today?"
            ).send()
        
        @cl.on_message
        async def main(message: cl.Message):
            """Handler for incoming messages."""
            try:
                # Send the message to the agent
                response = await agent.astart(message.content)
                
                # Send the response back
                await cl.Message(content=response).send()
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                await cl.Message(content=error_msg).send()
        
        return True
        
    except ImportError:
        logger.error("Chainlit not available. Install with: pip install chainlit")
        return False
