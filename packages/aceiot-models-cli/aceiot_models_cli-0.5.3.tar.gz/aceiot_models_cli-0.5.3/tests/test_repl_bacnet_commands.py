"""Tests for BACnet commands in REPL mode."""

import sys
from io import StringIO
from unittest.mock import Mock

from click import Context as ClickContext

from aceiot_models_cli.cli import cli
from aceiot_models_cli.repl.context import ContextType, ReplContext
from aceiot_models_cli.repl.executor_new import ReplCommandExecutor
from aceiot_models_cli.repl.parser import ParsedCommand


class TestReplBacnetCommands:
    """Test BACnet commands in REPL mode."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mocks
        self.mock_api_client = Mock()
        self.ctx = ClickContext(cli)
        self.ctx.obj = {"client": self.mock_api_client, "output": "table"}
        
        # Create executor and context
        self.executor = ReplCommandExecutor(cli, self.ctx)
        self.repl_context = ReplContext()
        
        # Sample gateway data
        self.gateway_data = {
            "name": "test-gateway",
            "site": "test-site",
            "client": "test-client",
            "deploy_config": {
                "deploy_bacnet": True,
                "trigger_scan": False,
                "trigger_deploy": False,
                "last_scan": "2024-01-01T00:00:00",
                "last_deploy": "2024-01-02T00:00:00",
                "bacnet_scan_address": "192.168.1.0/24",
                "bacnet_proxy_address": "192.168.1.1/24",
            }
        }
    
    def test_trigger_scan_in_gateway_context(self):
        """Test trigger-scan command auto-uses gateway context."""
        # Set up gateway context
        self.repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
        
        # Mock API responses
        self.mock_api_client.get_gateway.return_value = self.gateway_data.copy()
        self.mock_api_client.patch_gateway.return_value = {
            **self.gateway_data,
            "deploy_config": {
                **self.gateway_data["deploy_config"],
                "trigger_scan": True,
            }
        }
        
        # Create parsed command without gateway argument
        parsed_cmd = ParsedCommand(
            command_path=["gateways", "trigger-scan"],
            arguments=[],  # No gateway argument
            options={},
            context_args={},
            raw_input="gateways trigger-scan"
        )
        
        # Execute command and capture output
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            result = self.executor.execute(parsed_cmd, self.repl_context)
            output = captured_output.getvalue()
        finally:
            sys.stdout = original_stdout
        
        # Verify the gateway was auto-injected
        self.mock_api_client.get_gateway.assert_called_with("test-gateway")
        self.mock_api_client.patch_gateway.assert_called()
        assert "BACnet scan triggered" in output
    
    def test_deploy_points_in_gateway_context(self):
        """Test deploy-points command auto-uses gateway context."""
        # Set up gateway context
        self.repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
        
        # Mock API responses
        self.mock_api_client.get_gateway.return_value = self.gateway_data.copy()
        self.mock_api_client.patch_gateway.return_value = {
            **self.gateway_data,
            "deploy_config": {
                **self.gateway_data["deploy_config"],
                "trigger_deploy": True,
            }
        }
        
        # Create parsed command without gateway argument
        parsed_cmd = ParsedCommand(
            command_path=["gateways", "deploy-points"],
            arguments=[],
            options={},
            context_args={},
            raw_input="gateways deploy-points"
        )
        
        # Execute command and capture output
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            result = self.executor.execute(parsed_cmd, self.repl_context)
            output = captured_output.getvalue()
        finally:
            sys.stdout = original_stdout
        
        # Verify the gateway was auto-injected
        self.mock_api_client.get_gateway.assert_called_with("test-gateway")
        self.mock_api_client.patch_gateway.assert_called()
        assert "Point deployment triggered" in output
    
    def test_bacnet_status_in_gateway_context(self):
        """Test bacnet-status command auto-uses gateway context."""
        # Set up gateway context
        self.repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
        
        # Mock API response
        self.mock_api_client.get_gateway.return_value = self.gateway_data
        
        # Create parsed command without gateway argument
        parsed_cmd = ParsedCommand(
            command_path=["gateways", "bacnet-status"],
            arguments=[],
            options={},
            context_args={},
            raw_input="gateways bacnet-status"
        )
        
        # Execute command and capture output
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            result = self.executor.execute(parsed_cmd, self.repl_context)
            output = captured_output.getvalue()
        finally:
            sys.stdout = original_stdout
        
        # Verify the gateway was auto-injected
        self.mock_api_client.get_gateway.assert_called_with("test-gateway")
        assert "BACnet Status for Gateway: test-gateway" in output
        assert "BACnet Enabled: True" in output
    
    def test_enable_bacnet_in_gateway_context(self):
        """Test enable-bacnet command auto-uses gateway context."""
        # Set up gateway context
        self.repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
        
        # Mock API responses - start with disabled
        disabled_gateway = {
            **self.gateway_data,
            "deploy_config": {
                **self.gateway_data["deploy_config"],
                "deploy_bacnet": False,
            }
        }
        self.mock_api_client.get_gateway.return_value = disabled_gateway
        self.mock_api_client.patch_gateway.return_value = self.gateway_data  # Enabled
        
        # Create parsed command without gateway argument
        parsed_cmd = ParsedCommand(
            command_path=["gateways", "enable-bacnet"],
            arguments=[],
            options={},
            context_args={},
            raw_input="gateways enable-bacnet"
        )
        
        # Execute command and capture output
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            result = self.executor.execute(parsed_cmd, self.repl_context)
            output = captured_output.getvalue()
        finally:
            sys.stdout = original_stdout
        
        # Verify the gateway was auto-injected
        self.mock_api_client.get_gateway.assert_called_with("test-gateway")
        assert "BACnet enabled" in output
    
    def test_bacnet_command_with_explicit_gateway_overrides_context(self):
        """Test that explicit gateway argument overrides context."""
        # Set up gateway context
        self.repl_context.enter_context(ContextType.GATEWAY, "context-gateway")
        
        # Mock API response
        self.mock_api_client.get_gateway.return_value = self.gateway_data
        self.mock_api_client.patch_gateway.return_value = self.gateway_data
        
        # Create parsed command WITH gateway argument
        parsed_cmd = ParsedCommand(
            command_path=["gateways", "trigger-scan"],
            arguments=["explicit-gateway"],  # Explicit gateway
            options={},
            context_args={},
            raw_input="gateways trigger-scan explicit-gateway"
        )
        
        # Execute command and capture output
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            result = self.executor.execute(parsed_cmd, self.repl_context)
            output = captured_output.getvalue()
        finally:
            sys.stdout = original_stdout
        
        # Verify the explicit gateway was used, not context
        self.mock_api_client.get_gateway.assert_called_with("explicit-gateway")
    
    def test_trigger_scan_with_address_in_gateway_context(self):
        """Test trigger-scan with --scan-address option in gateway context."""
        # Set up gateway context
        self.repl_context.enter_context(ContextType.GATEWAY, "test-gateway")
        
        # Mock API responses
        self.mock_api_client.get_gateway.return_value = self.gateway_data.copy()
        self.mock_api_client.patch_gateway.return_value = {
            **self.gateway_data,
            "deploy_config": {
                **self.gateway_data["deploy_config"],
                "trigger_scan": True,
                "bacnet_scan_address": "192.168.2.0/24",
            }
        }
        
        # Create parsed command with scan-address option
        parsed_cmd = ParsedCommand(
            command_path=["gateways", "trigger-scan"],
            arguments=[],  # No gateway argument
            options={"scan-address": "192.168.2.0/24"},
            context_args={},
            raw_input="gateways trigger-scan --scan-address 192.168.2.0/24"
        )
        
        # Execute command and capture output
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            result = self.executor.execute(parsed_cmd, self.repl_context)
            output = captured_output.getvalue()
        finally:
            sys.stdout = original_stdout
        
        # Verify the gateway was auto-injected
        self.mock_api_client.get_gateway.assert_called_with("test-gateway")
        assert "BACnet scan triggered" in output
        assert "Scan address updated to: 192.168.2.0/24" in output
