"""Tests for base tool functionality."""

from typing import Annotated, Any

import pytest

from stanley.base_tool import (
    Tool,
    enforce_execute_type_annotations,
    get_openai_schema_from_fn,
)


class TestTool:
    """Test cases for Tool base class."""

    def test_tool_is_abstract(self):
        """Test that Tool cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Tool(name="test", description="test")

    def test_concrete_tool_implementation(self):
        """Test concrete tool implementation."""

        class TestTool(Tool):
            def execute(self, message: str) -> str:
                return f"Processed: {message}"

        tool = TestTool(name="test_tool", description="A test tool")
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.execute("hello") == "Processed: hello"

    def test_tool_schema_generation(self):
        """Test that tool generates correct schemas."""

        class TestTool(Tool):
            def execute(self, text: str, count: int = 1) -> str:
                return text * count

        tool = TestTool(name="repeat", description="Repeat text")

        # Check input schema
        assert tool.input_schema["type"] == "object"
        assert "text" in tool.input_schema["properties"]
        assert "count" in tool.input_schema["properties"]
        assert tool.input_schema["required"] == ["text"]

        # Tool should have required properties
        assert hasattr(tool, "input_schema")
        assert callable(tool.execute)

    def test_tool_with_complex_types(self):
        """Test tool with complex parameter types."""

        class ComplexTool(Tool):
            def execute(
                self,
                items: list[str],
                metadata: dict[str, int],
                optional: str | None = None,
            ) -> dict[str, Any]:
                return {"items": items, "metadata": metadata, "optional": optional}

        tool = ComplexTool(name="complex", description="Complex tool")

        schema = tool.input_schema
        assert schema["properties"]["items"]["type"] == "array"
        assert schema["properties"]["items"]["items"]["type"] == "string"
        assert schema["properties"]["metadata"]["type"] == "object"
        assert schema["properties"]["optional"]["nullable"] is True

    def test_tool_missing_annotations_raises(self):
        """Test that missing type annotations raise error."""
        with pytest.raises(TypeError, match="must have type annotations"):

            class BadTool(Tool):
                def execute(self, message):  # Missing type annotations
                    return message

            BadTool(name="bad", description="Bad tool")

    def test_tool_missing_return_annotation(self):
        """Test that missing return annotation raises error."""
        with pytest.raises(TypeError, match="must have a return type annotation"):

            class BadTool(Tool):
                def execute(self, message: str):  # Missing return annotation
                    return message

            BadTool(name="bad", description="Bad tool")


class TestGetOpenAISchemaFromFn:
    """Test schema generation from function signatures."""

    def test_basic_types(self):
        """Test basic type conversion."""

        def test_func(name: str, age: int, score: float, active: bool):
            pass

        schema = get_openai_schema_from_fn(test_func)

        assert schema["properties"]["name"]["type"] == "string"
        assert schema["properties"]["age"]["type"] == "integer"
        assert schema["properties"]["score"]["type"] == "number"
        assert schema["properties"]["active"]["type"] == "boolean"

    def test_annotated_descriptions(self):
        """Test Annotated types with descriptions."""

        def test_func(
            name: Annotated[str, "The user's name"], age: Annotated[int, "Age in years"]
        ):
            pass

        schema = get_openai_schema_from_fn(test_func)

        assert schema["properties"]["name"]["description"] == "The user's name"
        assert schema["properties"]["age"]["description"] == "Age in years"

    def test_optional_parameters(self):
        """Test optional parameters."""

        def test_func(required: str, optional: str = "default"):
            pass

        schema = get_openai_schema_from_fn(test_func)

        assert "required" in schema["required"]
        assert "optional" not in schema["required"]

    def test_list_types(self):
        """Test list type handling."""

        def test_func(items: list[str]):
            pass

        schema = get_openai_schema_from_fn(test_func)

        assert schema["properties"]["items"]["type"] == "array"
        assert schema["properties"]["items"]["items"]["type"] == "string"

    def test_dict_types(self):
        """Test dict type handling."""

        def test_func(mapping: dict[str, int]):
            pass

        schema = get_openai_schema_from_fn(test_func)

        assert schema["properties"]["mapping"]["type"] == "object"
        assert (
            schema["properties"]["mapping"]["additionalProperties"]["type"] == "integer"
        )


class TestEnforceExecuteTypeAnnotations:
    """Test type annotation enforcement."""

    def test_valid_annotations(self):
        """Test that valid annotations pass."""

        def execute(self, name: str, age: int) -> str:
            return f"{name} is {age}"

        # Should not raise
        enforce_execute_type_annotations(execute)

    def test_missing_parameter_annotations(self):
        """Test that missing parameter annotations raise error."""

        def execute(self, name, age: int):
            pass

        with pytest.raises(TypeError, match="Missing: \\['name'\\]"):
            enforce_execute_type_annotations(execute)

    def test_missing_return_annotation(self):
        """Test that missing return annotation raises error."""

        def execute(self, name: str):
            pass

        with pytest.raises(TypeError, match="must have a return type annotation"):
            enforce_execute_type_annotations(execute)

    def test_self_parameter_ignored(self):
        """Test that self parameter is ignored."""

        def execute(self, name: str) -> str:
            return name

        # Should not raise
        enforce_execute_type_annotations(execute)
