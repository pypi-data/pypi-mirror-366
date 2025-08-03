"""Tests for SendMessageToUser tool."""


from stanley.tools.send_message import SendMessageToUser


class TestSendMessageToUser:
    """Test cases for SendMessageToUser tool."""

    def test_initialization(self):
        """Test SendMessageToUser initialization."""
        tool = SendMessageToUser()
        assert tool.name == "send_message_to_user"
        assert tool.description == "Send a message to user and wait for response"
        assert "message" in tool.input_schema["properties"]
        assert tool.input_schema["properties"]["message"]["type"] == "string"

    def test_execute_basic(self):
        """Test basic execute functionality."""
        tool = SendMessageToUser()
        result = tool.execute("Hello, user!")
        assert result == "Hello, user!"

    def test_execute_empty_message(self):
        """Test execute with empty message."""
        tool = SendMessageToUser()
        result = tool.execute("")
        assert result == ""

    def test_execute_multiline_message(self):
        """Test execute with multiline message."""
        tool = SendMessageToUser()
        message = "Line 1\nLine 2\nLine 3"
        result = tool.execute(message)
        assert result == message

    def test_execute_unicode_message(self):
        """Test execute with unicode characters."""
        tool = SendMessageToUser()
        message = "Hello 🌍! 你好 世界"
        result = tool.execute(message)
        assert result == message

    def test_input_schema_structure(self):
        """Test the input schema structure."""
        tool = SendMessageToUser()
        schema = tool.input_schema

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "message" in schema["properties"]
        assert schema["properties"]["message"]["type"] == "string"
        assert schema["required"] == ["message"]

    def test_schema_completeness(self):
        """Test that tool has all required schema properties."""
        tool = SendMessageToUser()

        assert hasattr(tool, "input_schema")
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert callable(tool.execute)
