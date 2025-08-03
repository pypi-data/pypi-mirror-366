"""Integration tests for the agent framework."""

from unittest.mock import Mock, patch

import pytest

from stanlee import Agent, Tool


class TestAgentIntegration:
    """Integration tests for the complete agent workflow."""

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response with tool call."""
        response = Mock()
        message = Mock()
        tool_call = Mock()
        tool_call.id = "call_123"
        tool_call.function.name = "send_message_to_user"
        tool_call.function.arguments = '{"message": "Hello from agent!"}'

        message.tool_calls = [tool_call]
        message.model_dump.return_value = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_123",
                    "function": {
                        "name": "send_message_to_user",
                        "arguments": '{"message": "Hello from agent!"}',
                    },
                }
            ],
        }
        response.choices = [Mock(message=message)]
        return response

    def test_simple_agent_workflow(self, mock_llm_response):
        """Test complete agent workflow similar to example."""
        with patch("stanlee.agent.litellm.completion") as mock_completion:
            mock_completion.return_value = mock_llm_response

            agent = Agent(model="openai/gpt-4o-mini")
            responses = agent.run("Hi", stream=False)

            # Should have received responses
            assert len(responses) >= 1
            assert responses[0] == mock_llm_response

            # Check agent history contains expected messages
            messages = list(agent.history)
            roles = [msg["role"] for msg in messages]
            assert "system" in roles
            assert "user" in roles
            assert "assistant" in roles
            assert "tool" in roles

    def test_streaming_agent_workflow(self, mock_llm_response):
        """Test streaming agent workflow."""
        with patch("stanlee.agent.litellm.completion") as mock_completion:
            mock_completion.return_value = mock_llm_response

            agent = Agent(model="openai/gpt-4o-mini")
            responses = list(agent.run("Hi", stream=True))

            # Should have responses from streaming
            assert len(responses) >= 1

            # First response should be the LLM response
            assert responses[0] == mock_llm_response

    def test_custom_tool_integration(self, mock_llm_response):
        """Test agent with custom tool."""

        class WeatherTool(Tool):
            def execute(self, location: str) -> str:
                return f"Weather in {location}: Sunny, 25°C"

        # Modify mock to call weather tool
        tool_call = mock_llm_response.choices[0].message.tool_calls[0]
        tool_call.function.name = "weather_tool"
        tool_call.function.arguments = '{"location": "New York"}'

        with patch("stanlee.agent.litellm.completion") as mock_completion:
            mock_completion.return_value = mock_llm_response

            agent = Agent(model="openai/gpt-4o-mini")
            weather_tool = WeatherTool(name="weather_tool", description="Get weather")
            agent.tools.append(weather_tool)

            responses = list(agent.run("What's the weather in New York?", stream=True))

            # Should have processed the custom tool
            assert len(responses) >= 1

    def test_agent_error_handling(self):
        """Test agent handles errors gracefully."""
        with patch("stanlee.agent.litellm.completion") as mock_completion:
            # Simulate API error
            mock_completion.side_effect = Exception("API Error")

            agent = Agent(model="invalid-model")

            with pytest.raises(Exception):
                list(agent.run("Test", stream=True))

    def test_agent_with_no_tool_calls(self):
        """Test agent response without tool calls."""
        response = Mock()
        message = Mock()
        message.tool_calls = []  # No tool calls
        message.model_dump.return_value = {
            "role": "assistant",
            "content": "Just a regular response",
        }
        response.choices = [Mock(message=message)]

        with patch("stanlee.agent.litellm.completion") as mock_completion:
            mock_completion.return_value = response

            agent = Agent(model="openai/gpt-4o-mini")

            # Take only first few responses since it will continue for 20 steps
            responses = []
            for i, response_item in enumerate(agent.run("Hi", stream=True)):
                responses.append(response_item)
                if i >= 2:  # Just take first few
                    break

            # Should have gotten responses
            assert len(responses) >= 1
            assert responses[0] == response

    def test_multiple_tool_calls(self):
        """Test agent handling multiple tool calls in one response."""
        response = Mock()
        message = Mock()

        # Create multiple tool calls
        tool_call_1 = Mock()
        tool_call_1.id = "call_1"
        tool_call_1.function.name = "send_message_to_user"
        tool_call_1.function.arguments = '{"message": "First message"}'

        tool_call_2 = Mock()
        tool_call_2.id = "call_2"
        tool_call_2.function.name = "send_message_to_user"
        tool_call_2.function.arguments = '{"message": "Second message"}'

        message.tool_calls = [tool_call_1, tool_call_2]
        message.model_dump.return_value = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_1",
                    "function": {
                        "name": "send_message_to_user",
                        "arguments": '{"message": "First message"}',
                    },
                },
                {
                    "id": "call_2",
                    "function": {
                        "name": "send_message_to_user",
                        "arguments": '{"message": "Second message"}',
                    },
                },
            ],
        }
        response.choices = [Mock(message=message)]

        with patch("stanlee.agent.litellm.completion") as mock_completion:
            mock_completion.return_value = response

            agent = Agent(model="openai/gpt-4o-mini")
            responses = list(agent.run("Hi", stream=True))

            # Should handle multiple tool calls
            assert len(responses) == 2  # response + tool messages
            assert responses[0] == response
            assert isinstance(responses[1], list)  # Tool messages
            assert len(responses[1]) == 2  # Two tool calls

    def test_agent_history_persistence(self, mock_llm_response):
        """Test that agent history persists across runs."""
        with patch("stanlee.agent.litellm.completion") as mock_completion:
            mock_completion.return_value = mock_llm_response

            agent = Agent(model="openai/gpt-4o-mini")

            # First interaction
            list(agent.run("First message", stream=True))
            first_history_len = len(agent.history)

            # Second interaction
            list(agent.run("Second message", stream=True))
            second_history_len = len(agent.history)

            # History should have grown
            assert second_history_len > first_history_len

            # Should contain messages from both interactions
            messages = [msg["content"] for msg in agent.history if msg.get("content")]
            assert any("First message" in str(msg) for msg in messages)
            assert any("Second message" in str(msg) for msg in messages)
