"""Tests for the Agent class."""

from unittest.mock import Mock, patch

import pytest

from stanley.agent import Agent, BaseAgent
from stanley.base_tool import Tool
from stanley.errors import SystemPromptError


class TestBaseAgent:
    """Test cases for BaseAgent class."""

    def test_base_agent_initialization(self):
        """Test that BaseAgent initializes correctly."""
        with patch.object(BaseAgent, "setup_system_prompt", return_value="Test prompt"):
            agent = BaseAgent()
            assert agent._system_prompt == "Test prompt"
            assert agent._step_idx == 0
            assert len(agent.tools) == 1  # Should have SendMessageToUser

    def test_system_prompt_property(self):
        """Test system prompt getter and setter."""
        with patch.object(BaseAgent, "setup_system_prompt", return_value="Test prompt"):
            agent = BaseAgent()
            assert agent.system_prompt == "Test prompt"

            with pytest.raises(SystemPromptError):
                agent.system_prompt = "New prompt"

    def test_setup_system_prompt(self):
        """Test loading system prompt from file."""
        agent = BaseAgent()
        assert isinstance(agent._system_prompt, str)
        assert len(agent._system_prompt) > 0

    def test_abstract_run_one_step(self):
        """Test that _run_one_step is abstract."""
        agent = BaseAgent()
        with pytest.raises(NotImplementedError):
            agent._run_one_step()


class TestAgent:
    """Test cases for Agent class."""

    @pytest.fixture
    def mock_litellm(self):
        """Mock litellm completion."""
        with patch("stanlee.agent.litellm.completion") as mock:
            yield mock

    @pytest.fixture
    def mock_response(self):
        """Create a mock LLM response."""
        response = Mock()
        message = Mock()
        message.model_dump.return_value = {
            "role": "assistant",
            "content": "Test response",
        }
        message.tool_calls = []
        response.choices = [Mock(message=message)]
        return response

    def test_agent_initialization(self):
        """Test Agent initialization."""
        agent = Agent(model="gpt-4")
        assert agent.model == "gpt-4"
        assert agent._step_idx == 0
        assert len(agent.history) > 0  # Should have system prompt
        assert len(agent.tools) == 1  # Should have SendMessageToUser

    def test_agent_with_system_prompt(self):
        """Test agent adds system prompt to history."""
        agent = Agent(model="gpt-4")
        messages = list(agent.history)
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == agent._system_prompt

    def test_tools_for_llm_property(self):
        """Test tools_for_llm returns correct format."""
        agent = Agent(model="gpt-4")

        # Add a custom tool
        custom_tool = Mock(spec=Tool)
        custom_tool.name = "test_tool"
        custom_tool.description = "A test tool"
        custom_tool.input_schema = {"type": "object", "properties": {}}
        agent.tools.append(custom_tool)

        tools_for_llm = agent.tools_for_llm
        assert len(tools_for_llm) == 2  # SendMessageToUser + custom_tool

        # Check format
        for tool in tools_for_llm:
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]

    def test_run_with_stream(self, mock_litellm, mock_response):
        """Test running agent with streaming."""
        mock_litellm.return_value = mock_response

        agent = Agent(model="gpt-4")
        result_gen = agent.run("Hello", stream=True)

        # Should return a generator
        assert hasattr(result_gen, "__iter__")

        # Consume one step
        result = next(result_gen)
        assert result == mock_response

    def test_run_without_stream(self, mock_litellm, mock_response):
        """Test running agent without streaming."""
        mock_litellm.return_value = mock_response

        agent = Agent(model="gpt-4")
        results = agent.run("Hello", stream=False)

        # Should return a list
        assert isinstance(results, list)
        assert len(results) > 0

    def test_run_one_step_basic(self, mock_litellm, mock_response):
        """Test _run_one_step basic functionality."""
        mock_litellm.return_value = mock_response

        agent = Agent(model="gpt-4")
        agent.history.add_message({"role": "user", "content": "Test"})

        results = list(agent._run_one_step())
        assert len(results) == 1
        assert results[0] == mock_response

        # Check history was updated
        assert len(agent.history) == 3  # system + user + assistant

    def test_run_one_step_with_tool_calls(self, mock_litellm):
        """Test _run_one_step with tool calls."""
        # Create mock response with tool calls
        response = Mock()
        message = Mock()
        tool_call = Mock()
        tool_call.id = "call_123"
        tool_call.function.name = "send_message_to_user"
        tool_call.function.arguments = '{"message": "Hello user"}'

        message.tool_calls = [tool_call]
        message.model_dump.return_value = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_123",
                    "function": {
                        "name": "send_message_to_user",
                        "arguments": '{"message": "Hello user"}',
                    },
                }
            ],
        }
        response.choices = [Mock(message=message)]
        mock_litellm.return_value = response

        agent = Agent(model="gpt-4")
        agent.history.add_message({"role": "user", "content": "Test"})

        # Mock the execute_tool_call method
        with patch.object(agent, "execute_tool_call", return_value="Tool executed"):
            results = list(agent._run_one_step())

        assert len(results) == 2  # response + tool messages
        assert results[0] == response
        assert isinstance(results[1], list)
        assert len(results[1]) == 1  # One tool message

        # Should stop after send_message_to_user
        assert not agent._should_continue

    def test_execute_tool_call(self):
        """Test executing a tool call."""
        agent = Agent(model="gpt-4")

        # Create a mock tool
        mock_tool = Mock(spec=Tool)
        mock_tool.name = "test_tool"
        mock_tool.execute.return_value = "Tool result"
        agent.tools.append(mock_tool)

        # Create a tool call
        tool_call = Mock()
        tool_call.function.name = "test_tool"
        tool_call.function.arguments = '{"param": "value"}'

        result = agent.execute_tool_call(tool_call)
        assert result == "Tool result"
        mock_tool.execute.assert_called_once_with(param="value")

    def test_execute_tool_call_not_found(self):
        """Test executing a tool call for non-existent tool."""
        agent = Agent(model="gpt-4")

        tool_call = Mock()
        tool_call.function.name = "non_existent_tool"
        tool_call.function.arguments = "{}"

        with pytest.raises(ValueError, match="Tool 'non_existent_tool' not found"):
            agent.execute_tool_call(tool_call)

    def test_execute_tool_call_with_dict_args(self):
        """Test executing a tool call with dict arguments."""
        agent = Agent(model="gpt-4")

        mock_tool = Mock(spec=Tool)
        mock_tool.name = "test_tool"
        mock_tool.execute.return_value = "Tool result"
        agent.tools.append(mock_tool)

        tool_call = Mock()
        tool_call.function.name = "test_tool"
        tool_call.function.arguments = {"param": "value"}  # Dict instead of string

        result = agent.execute_tool_call(tool_call)
        assert result == "Tool result"
        mock_tool.execute.assert_called_once_with(param="value")

    def test_max_steps_limit(self, mock_litellm, mock_response):
        """Test that agent respects max steps limit."""
        mock_litellm.return_value = mock_response

        agent = Agent(model="gpt-4")

        count = 0
        for _ in agent.run("Test", stream=True):
            count += 1
            if count > 25:
                break

        assert count == 20

    def test_history_management(self, mock_litellm, mock_response):
        """Test that history is properly managed."""
        mock_litellm.return_value = mock_response

        agent = Agent(model="gpt-4")
        initial_history_len = len(agent.history)

        # Run one interaction
        list(agent.run("Hello", stream=True))

        # History should have grown
        assert len(agent.history) > initial_history_len

        # Check message types
        messages = list(agent.history)
        roles = [msg["role"] for msg in messages]
        assert "system" in roles
        assert "user" in roles
        assert "assistant" in roles
