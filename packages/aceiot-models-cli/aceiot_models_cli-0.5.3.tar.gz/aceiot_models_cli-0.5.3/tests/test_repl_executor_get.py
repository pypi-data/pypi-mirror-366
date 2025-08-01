"""Test that get command is properly routed in REPL executor."""

from unittest.mock import Mock

import pytest
from click import Context as ClickContext

from aceiot_models_cli.cli import cli
from aceiot_models_cli.repl.context import ContextType, ReplContext
from aceiot_models_cli.repl.executor_new import ReplCommandExecutor
from aceiot_models_cli.repl.parser import ParsedCommand


def test_get_command_is_handled_as_repl_command():
    """Test that 'get' command is routed to REPL command handler."""
    # Create mocks
    mock_api_client = Mock()
    ctx = ClickContext(cli)
    ctx.obj = {"client": mock_api_client, "output": "json"}
    
    # Create executor and context
    executor = ReplCommandExecutor(cli, ctx)
    repl_context = ReplContext()
    
    # Set up gateway context
    repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
    
    # Mock API response
    mock_api_client.get_gateway.return_value = {
        "name": "test-gateway",
        "nice_name": "Test Gateway",
        "id": "123",
    }
    
    # Create parsed command for 'get'
    parsed_cmd = ParsedCommand(
        command_path=["get"],
        arguments=["-o", "table"],
        options={},
        context_args={},
        raw_input="get -o table"
    )
    
    # Execute through main execute method
    result = executor.execute(parsed_cmd, repl_context)
    
    # Should not raise "Command not found" error
    assert "Command not found" not in str(result)
    # Should contain gateway info
    assert "Gateway: test-gateway" in result or "test-gateway" in result
