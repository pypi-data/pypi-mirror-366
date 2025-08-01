"""
Comprehensive tests for ShaheenAI core functionality
====================================================

This module tests the core components of ShaheenAI including Agent, MCP, and tools.
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from shaheenai import Agent, Config, MCP, tool
from shaheenai.research import ResearchPlanner, BibliographyManager, ResearchProject, ResearchTemplates


class TestAgent:
    """Test cases for the Agent class."""
    
    def test_agent_initialization(self):
        """Test basic agent initialization."""
        agent = Agent(
            name="TestAgent",
            instructions="You are a test agent.",
            llm="openrouter/anthropic/claude-3.5-sonnet"
        )
        
        assert agent.config.name == "TestAgent"
        assert agent.config.instructions == "You are a test agent."
        assert agent.config.llm == "openrouter/anthropic/claude-3.5-sonnet"
        assert agent.config.memory == False
        assert agent.config.self_reflection == False
    
    def test_agent_with_memory(self):
        """Test agent with memory enabled."""
        agent = Agent(
            instructions="You are a helpful assistant.",
            memory=True
        )
        
        assert agent.config.memory == True
        assert isinstance(agent.conversation_history, list)
        assert len(agent.conversation_history) == 0
    
    def test_agent_identity_response(self):
        """Test agent identity responses."""
        agent = Agent()
        
        # Test various identity questions
        identity_questions = [
            "who are you",
            "who developed you",
            "who created you",
            "what are you",
            "tell me about yourself"
        ]
        
        for question in identity_questions:
            response = agent._identity_response(question)
            assert response is not None
            assert "Shaheen AI" in response
            assert "Engr. Hamza" in response
    
    def test_memory_management(self):
        """Test conversation memory functionality."""
        agent = Agent(memory=True)
        
        # Test adding to memory
        agent.conversation_history.append({"role": "user", "content": "Hello"})
        agent.conversation_history.append({"role": "assistant", "content": "Hi there!"})
        
        assert len(agent.get_memory()) == 2
        
        # Test clearing memory
        agent.clear_memory()
        assert len(agent.get_memory()) == 0
    
    def test_tool_loading(self):
        """Test tool loading functionality."""
        agent = Agent(tools=["calculate"])
        
        # The agent should attempt to load tools from registry
        assert isinstance(agent.tools, dict)
    
    @patch('shaheenai.agent.LLMProviderFactory.create_provider')
    def test_message_building(self, mock_provider):
        """Test message building for LLM calls."""
        mock_llm = Mock()
        mock_provider.return_value = mock_llm
        
        agent = Agent(instructions="Test instructions")
        messages = agent._build_messages("Hello")
        
        assert len(messages) >= 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "Test instructions"
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "Hello"


class TestMCP:
    """Test cases for the MCP (Model Context Protocol) system."""
    
    def test_mcp_initialization(self):
        """Test MCP server initialization."""
        mcp = MCP(host="localhost", port=8080)
        
        assert mcp.host == "localhost"
        assert mcp.port == 8080
        assert mcp.registry is not None
    
    def test_tool_decorator(self):
        """Test the @tool decorator functionality."""
        
        @tool(description="Test tool for addition")
        def add_numbers(a: int, b: int) -> int:
            """Add two numbers together."""
            return a + b
        
        # Test that the tool was registered
        from shaheenai.mcp import get_tool_registry
        registry = get_tool_registry()
        
        assert "add_numbers" in registry.list_tools()
        tool_def = registry.get_tool("add_numbers")
        assert tool_def is not None
        assert tool_def.name == "add_numbers"
        assert "addition" in tool_def.description.lower()
    
    def test_tool_execution(self):
        """Test tool execution through MCP."""
        
        @tool()
        def multiply(x: float, y: float) -> float:
            """Multiply two numbers."""
            return x * y
        
        mcp = MCP()
        result = asyncio.run(mcp.call_tool("multiply", x=3.5, y=2.0))
        
        assert result == 7.0
    
    def test_built_in_calculator(self):
        """Test the built-in calculator tool."""
        from shaheenai.mcp import get_tool_registry
        
        registry = get_tool_registry()
        assert "calculate" in registry.list_tools()
        
        calc_tool = registry.get_tool("calculate")
        result = calc_tool.function("2 + 3 * 4")
        
        assert "14" in str(result)  # 2 + (3 * 4) = 14


class TestResearchModule:
    """Test cases for the research planning module."""
    
    def test_research_planner(self):
        """Test research planner functionality."""
        planner = ResearchPlanner()
        
        # Test adding tasks
        planner.add_task("Literature review")
        planner.add_task("Data collection")
        
        tasks = planner.view_tasks()
        assert len(tasks) == 2
        assert "Literature review" in tasks
        assert "Data collection" in tasks
        
        # Test timeline setting
        planner.set_timeline("Literature review", "2024-08-15")
        timeline = planner.view_timeline()
        
        assert "Literature review" in timeline
        assert timeline["Literature review"] == "2024-08-15"
    
    def test_bibliography_manager(self):
        """Test bibliography management functionality."""
        bib_manager = BibliographyManager()
        
        # Test adding entries
        entry1 = {
            "type": "article",
            "key": "smith2023",
            "title": "AI in Research",
            "author": "Smith, J.",
            "year": "2023"
        }
        
        bib_manager.add_entry(entry1)
        entries = bib_manager.get_entries()
        
        assert len(entries) == 1
        assert entries[0]["title"] == "AI in Research"
        assert entries[0]["author"] == "Smith, J."
    
    def test_research_project(self):
        """Test research project management."""
        project = ResearchProject(
            name="AI Research Project",
            description="Study of AI applications",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
        
        # Test basic properties
        assert project.name == "AI Research Project"
        assert project.description == "Study of AI applications"
        
        # Test adding milestones
        project.add_milestone(
            "Literature Review",
            "Complete comprehensive literature review",
            datetime(2024, 3, 1)
        )
        
        assert len(project.milestones) == 1
        assert project.milestones[0].name == "Literature Review"
        
        # Test progress calculation
        progress = project.get_progress()
        assert progress == 0.0  # No completed milestones
        
        # Complete a milestone
        success = project.complete_milestone("Literature Review")
        assert success == True
        
        progress = project.get_progress()
        assert progress == 100.0  # 1 out of 1 milestone completed
        
        # Test adding notes
        project.add_note("This is a research note")
        assert len(project.notes) == 1
        assert "research note" in project.notes[0]
        
        # Test adding tags
        project.add_tag("machine-learning")
        project.add_tag("nlp")
        assert "machine-learning" in project.tags
        assert "nlp" in project.tags
        
        # Test report generation
        report = project.generate_report()
        assert "AI Research Project" in report
        assert "Literature Review" in report
        assert "100.0% complete" in report
    
    def test_research_templates(self):
        """Test research template generation."""
        # Test proposal template
        proposal = ResearchTemplates.generate_template("proposal")
        assert "Research Proposal Template" in proposal
        assert "Abstract" in proposal
        assert "Methodology" in proposal
        
        # Test report template
        report = ResearchTemplates.generate_template("report")
        assert "Research Report Template" in report
        assert "Results" in report
        assert "Conclusion" in report
        
        # Test invalid template
        invalid = ResearchTemplates.generate_template("nonexistent")
        assert "Template not found" in invalid


class TestTools:
    """Test cases for built-in tools."""
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_weather_tool_mock(self, mock_client):
        """Test weather tool with mocked API response."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {
                "temp": 20.5,
                "feels_like": 18.0,
                "humidity": 65,
                "pressure": 1013,
                "temp_min": 18.0,
                "temp_max": 23.0
            },
            "weather": [{"main": "Clouds", "description": "broken clouds"}],
            "wind": {"speed": 3.5, "deg": 180},
            "clouds": {"all": 40},
            "visibility": 10000
        }
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client.return_value = mock_client_instance
        
        from shaheenai.mcp import get_weather
        
        with patch.dict(os.environ, {'OPENWEATHER_API_KEY': 'test_key'}):
            result = await get_weather("London")
            
            assert "London, GB" in result
            assert "20.5°C" in result
            assert "Broken clouds" in result
    
    @pytest.mark.asyncio
    async def test_web_search_tool_fallback(self):
        """Test web search tool fallback behavior."""
        from shaheenai.mcp import web_search
        
        # Test without API keys (should use fallback)
        with patch.dict(os.environ, {}, clear=True):
            result = await web_search("Python programming")
            
            assert "Search for 'Python programming'" in result
            assert "BRAVE_API_KEY" in result or "Unable to perform web search" in result
    
    def test_calculate_tool(self):
        """Test calculator tool functionality."""
        from shaheenai.mcp import calculate
        
        # Test basic arithmetic
        result = calculate("2 + 3")
        assert "5" in result
        
        result = calculate("10 * 5")
        assert "50" in result
        
        result = calculate("100 / 4")
        assert "25" in result
        
        # Test with invalid expression
        result = calculate("invalid expression")
        assert "Error" in result


class TestIntegration:
    """Integration tests for the complete library."""
    
    @patch('shaheenai.llm_providers.openrouter.OpenRouterProvider.generate')
    def test_agent_with_tools_integration(self, mock_generate):
        """Test agent working with tools."""
        mock_generate.return_value = "The calculation result is 42."
        
        agent = Agent(
            instructions="You are a helpful calculator assistant.",
            tools=["calculate"]
        )
        
        # Test that tools are loaded
        assert len(agent.tools) > 0
    
    def test_research_workflow_integration(self):
        """Test complete research workflow."""
        # Create a research project
        project = ResearchProject(
            name="Machine Learning Study",
            description="Comprehensive ML research",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 6, 30)
        )
        
        # Add milestones
        project.add_milestone("Data Collection", "Gather training data", datetime(2024, 2, 1))
        project.add_milestone("Model Training", "Train ML models", datetime(2024, 4, 1))
        project.add_milestone("Evaluation", "Evaluate model performance", datetime(2024, 5, 1))
        
        # Add bibliography entries
        bib_manager = BibliographyManager()
        bib_manager.add_entry({
            "type": "article",
            "key": "lecun2015",
            "title": "Deep Learning",
            "author": "LeCun, Y. and Bengio, Y. and Hinton, G.",
            "year": "2015"
        })
        
        # Create planner
        planner = ResearchPlanner()
        planner.add_task("Literature Review")
        planner.add_task("Experiment Design")
        
        # Verify integration
        assert len(project.milestones) == 3
        assert len(bib_manager.get_entries()) == 1
        assert len(planner.view_tasks()) == 2
        
        # Test project progress
        project.complete_milestone("Data Collection")
        assert project.get_progress() == 33.33333333333333  # 1/3 completed
    
    def test_library_imports(self):
        """Test that all main components can be imported successfully."""
        from shaheenai import Agent, Config, MCP, tool
        from shaheenai.research import ResearchPlanner, BibliographyManager, ResearchProject, ResearchTemplates
        
        # Test that classes can be instantiated
        agent = Agent()
        mcp = MCP()
        planner = ResearchPlanner()
        bib_manager = BibliographyManager()
        
        assert agent is not None
        assert mcp is not None
        assert planner is not None
        assert bib_manager is not None


# Pytest fixtures for common test data
@pytest.fixture
def sample_research_project():
    """Fixture providing a sample research project."""
    return ResearchProject(
        name="Test Project",
        description="A test research project",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )


@pytest.fixture
def sample_agent():
    """Fixture providing a sample agent."""
    return Agent(
        name="TestAgent",
        instructions="You are a test assistant.",
        memory=True
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
