"""Tests for context-aware help in REPL mode."""

from unittest.mock import Mock

from click import Context as ClickContext

from aceiot_models_cli.cli import cli
from aceiot_models_cli.repl.context import ContextType, ReplContext
from aceiot_models_cli.repl.executor_new import ReplCommandExecutor
from aceiot_models_cli.repl.parser import ParsedCommand


class TestReplContextHelp:
    """Test context-aware help in REPL mode."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mocks
        self.mock_api_client = Mock()
        self.ctx = ClickContext(cli)
        self.ctx.obj = {"client": self.mock_api_client, "output": "table"}
        
        # Create executor and context
        self.executor = ReplCommandExecutor(cli, self.ctx)
        self.repl_context = ReplContext()
    
    def test_help_in_global_context(self):
        """Test help command in global context."""
        # Create parsed command
        parsed_cmd = ParsedCommand(
            command_path=["help"],
            arguments=[],
            options={},
            context_args={},
            raw_input="help"
        )
        
        # Execute command
        result = self.executor.execute(parsed_cmd, self.repl_context)
        
        # Verify general help is shown
        assert "ACE IoT Models CLI - Interactive Mode" in result
        assert "REPL Commands:" in result
        assert "Context Types:" in result
        
        # Verify no context-specific help is shown
        assert "Gateway Context Commands:" not in result
        assert "Site Context Commands:" not in result
        assert "Client Context Commands:" not in result
    
    def test_help_in_gateway_context(self):
        """Test help command in gateway context shows BACnet commands."""
        # Set up gateway context
        self.repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
        
        # Create parsed command
        parsed_cmd = ParsedCommand(
            command_path=["help"],
            arguments=[],
            options={},
            context_args={},
            raw_input="help"
        )
        
        # Execute command
        result = self.executor.execute(parsed_cmd, self.repl_context)
        
        # Verify general help is shown
        assert "ACE IoT Models CLI - Interactive Mode" in result
        
        # Verify gateway context help is shown with direct commands
        assert "Gateway Context Commands:" in result
        assert "get" in result
        assert "trigger-scan" in result
        assert "deploy-points" in result
        assert "enable-bacnet" in result
        assert "disable-bacnet" in result
        assert "bacnet-status" in result
        
        # Verify BACnet examples are shown
        assert "BACnet Examples:" in result
        assert "--scan-address 192.168.1.0/24" in result
        assert "Note: You can also use the full 'gateways <command>' form if needed." in result
    
    def test_help_in_site_context(self):
        """Test help command in site context."""
        # Set up site context
        self.repl_context.enter_context(ContextType.SITE, "test-site")
        
        # Create parsed command
        parsed_cmd = ParsedCommand(
            command_path=["help"],
            arguments=[],
            options={},
            context_args={},
            raw_input="help"
        )
        
        # Execute command
        result = self.executor.execute(parsed_cmd, self.repl_context)
        
        # Verify site context help is shown
        assert "Site Context Commands:" in result
        assert "sites get" in result
        assert "points list" in result
        
        # Verify other context help is not shown
        assert "Gateway Context Commands:" not in result
        assert "Client Context Commands:" not in result
    
    def test_help_in_client_context(self):
        """Test help command in client context."""
        # Set up client context
        self.repl_context.enter_context(ContextType.CLIENT, "test-client")
        
        # Create parsed command
        parsed_cmd = ParsedCommand(
            command_path=["help"],
            arguments=[],
            options={},
            context_args={},
            raw_input="help"
        )
        
        # Execute command
        result = self.executor.execute(parsed_cmd, self.repl_context)
        
        # Verify client context help is shown
        assert "Client Context Commands:" in result
        assert "clients get" in result
        assert "sites list" in result
        
        # Verify other context help is not shown
        assert "Gateway Context Commands:" not in result
        assert "Site Context Commands:" not in result
