"""
CLI module for ShaheenAI
========================

This module provides command-line interface functionality for running
agents, managing configurations, and interacting with the ShaheenAI library.
"""

import os
import sys
import yaml
import click
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from .agent import Agent
from .config import Config
from .version import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(verbose: bool):
    """
    ShaheenAI - A flexible, multi-LLM, agent-oriented Python library.
    
    Author: Hamza
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--llm', '-l', help='Override LLM provider (e.g., openai/gpt-4)')
@click.option('--temperature', '-t', type=float, help='Override temperature setting')
@click.option('--max-tokens', '-m', type=int, help='Override max tokens setting')
def run(config_file: str, llm: Optional[str], temperature: Optional[float], max_tokens: Optional[int]):
    """
    Run agents from a YAML configuration file.
    
    Example:
        shaheenai run agents.yaml
        shaheenai run agents.yaml --llm openai/gpt-4 --temperature 0.8
    """
    try:
        # Load configuration
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration from {config_file}")
        
        # Extract agents configuration
        agents_config = config_data.get('agents', {})
        if not agents_config:
            click.echo("Error: No agents found in configuration file")
            sys.exit(1)
        
        # Run each agent
        for agent_name, agent_config in agents_config.items():
            click.echo(f"\n--- Starting agent: {agent_name} ---")
            
            # Apply CLI overrides
            if llm:
                agent_config['llm'] = llm
            if temperature is not None:
                agent_config['temperature'] = temperature
            if max_tokens is not None:
                agent_config['max_tokens'] = max_tokens
            
            # Create and run agent  
            agent = Agent(**agent_config)
            
            # Get tasks for this agent
            tasks = agent_config.get('tasks', [])
            if not tasks:
                click.echo(f"No tasks defined for agent {agent_name}")
                continue
            
            # Execute tasks
            for i, task in enumerate(tasks, 1):
                click.echo(f"\nTask {i}: {task}")
                try:
                    response = agent.start(task)
                    click.echo(f"Response: {response}")
                except Exception as e:
                    click.echo(f"Error executing task: {e}")
        
    except Exception as e:
        click.echo(f"Error running configuration: {e}")
        sys.exit(1)


@main.command()
@click.argument('prompt')
@click.option('--llm', '-l', default='openai/gpt-3.5-turbo', help='LLM provider to use')
@click.option('--temperature', '-t', type=float, default=0.7, help='Temperature setting')
@click.option('--max-tokens', '-m', type=int, default=1000, help='Maximum tokens')
@click.option('--reflection', '-r', is_flag=True, help='Enable self-reflection')
@click.option('--memory', is_flag=True, help='Enable conversation memory')
def auto(prompt: str, llm: str, temperature: float, max_tokens: int, reflection: bool, memory: bool):
    """
    Auto-mode: Run a single prompt with an agent.
    
    Example:
        shaheenai auto "Write a summary about AI"
        shaheenai auto "What's the weather like?" --llm groq/llama-3.1-8b-instant
    """
    try:
        # Create agent with specified configuration
        agent = Agent(
            instructions="You are a helpful AI assistant.",
            llm=llm,
            temperature=temperature,
            max_tokens=max_tokens,
            self_reflection=reflection,
            memory=memory
        )
        
        click.echo(f"Using LLM: {llm}")
        click.echo(f"Prompt: {prompt}\n")
        
        # Generate response
        response = agent.start(prompt)
        click.echo(f"Response: {response}")
        
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


@main.command()
def providers():
    """List supported LLM providers."""
    from .llm_providers.factory import LLMProviderFactory
    
    supported = LLMProviderFactory.list_supported_providers()
    
    click.echo("Supported LLM providers:")
    for provider in supported:
        available = "✓" if LLMProviderFactory.is_provider_available(provider) else "✗"
        click.echo(f"  {available} {provider}")
    
    click.echo("\nNote: ✓ = dependencies installed, ✗ = requires installation")
    click.echo("Install with: pip install shaheenai[provider_name]")


@main.command()
@click.option('--chainlit', is_flag=True, help='Start Chainlit UI')
@click.option('--streamlit', is_flag=True, help='Start Streamlit UI')
@click.option('--port', '-p', type=int, default=8000, help='Port to run UI on')
def ui(chainlit: bool, streamlit: bool, port: int):
    """
    Start interactive UI for ShaheenAI.
    
    Example:
        shaheenai ui --chainlit
        shaheenai ui --streamlit --port 8501
    """
    if chainlit:
        try:
            import subprocess
            # Look for chainlit app in the package
            app_path = Path(__file__).parent / "ui" / "chainlit_app.py"
            if app_path.exists():
                subprocess.run(["chainlit", "run", str(app_path), "--port", str(port)])
            else:
                click.echo("Chainlit app not found. Create chainlit_app.py to use this feature.")
        except ImportError:
            click.echo("Chainlit not installed. Install with: pip install shaheenai[chainlit]")
    
    elif streamlit:
        try:
            import subprocess
            # Look for streamlit app in the package
            app_path = Path(__file__).parent / "ui" / "streamlit_app.py" 
            if app_path.exists():
                subprocess.run(["streamlit", "run", str(app_path), "--server.port", str(port)])
            else:
                click.echo("Streamlit app not found. Create streamlit_app.py to use this feature.")
        except ImportError:
            click.echo("Streamlit not installed. Install with: pip install shaheenai[streamlit]")
    
    else:
        click.echo("Please specify --chainlit or --streamlit")


@main.command()
def init():
    """Initialize a new ShaheenAI project with example files."""
    
    # Create example agents.yaml
    agents_yaml = """
agents:
  writer:
    llm: "openai/gpt-3.5-turbo"
    instructions: "You are a creative writer who creates engaging content."
    temperature: 0.8
    max_tokens: 1000
    tasks:
      - "Write a short story about AI and humans working together"
      - "Create a blog post about the future of technology"
  
  analyst:
    llm: "groq/llama-3.1-8b-instant" 
    instructions: "You are a data analyst who provides insights and analysis."
    temperature: 0.3
    max_tokens: 800
    self_reflection: true
    tasks:
      - "Analyze current trends in artificial intelligence"
      - "Provide insights on market opportunities in AI"
"""
    
    # Create example Python script
    example_py = '''
from shaheenai import Agent, MCP, tool

# Define a custom tool
@tool(description="Get current weather for a location")
async def get_weather(location: str) -> str:
    """Get weather information for a specific location."""
    # This would normally call a real weather API
    return f"Weather in {location}: Sunny, 25°C"

# Create and run agent
def main():
    agent = Agent(
        instructions="You are a helpful assistant with access to weather information.",
        llm="openai/gpt-3.5-turbo",
        tools=["get_weather"],
        memory=True,
        self_reflection=True
    )
    
    response = agent.start("What's the weather like in London?")
    print(f"Agent response: {response}")

if __name__ == "__main__":
    main()
'''
    
    # Write files
    try:
        with open("agents.yaml", "w") as f:
            f.write(agents_yaml.strip())
        
        with open("example_agent.py", "w") as f:
            f.write(example_py.strip())
        
        click.echo("✓ Created agents.yaml")
        click.echo("✓ Created example_agent.py")
        click.echo("\nTo get started:")
        click.echo("1. Set your API keys (e.g., export OPENAI_API_KEY=your_key)")
        click.echo("2. Run: shaheenai run agents.yaml")
        click.echo("3. Or run: python example_agent.py")
        
    except Exception as e:
        click.echo(f"Error creating files: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
