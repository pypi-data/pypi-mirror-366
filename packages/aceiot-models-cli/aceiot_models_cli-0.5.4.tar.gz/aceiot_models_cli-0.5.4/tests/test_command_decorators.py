"""Comprehensive tests for command decorators."""

from unittest.mock import Mock, patch

import click
import pytest

from aceiot_models_cli.commands.base import (
    BaseCommand,
    CommandMetadata,
    CommandScope,
    ContextAwareCommand,
    command_registry,
)
from aceiot_models_cli.commands.decorators import click_command_adapter, command, context_command, repl_command
from aceiot_models_cli.repl.context import ContextType, ReplContext


class TestCommandDecorator:
    """Test the @command decorator."""
    
    def setup_method(self):
        """Clear registry before each test."""
        command_registry._commands.clear()
        command_registry._aliases.clear()
        command_registry._context_commands.clear()
    
    def test_basic_command_registration(self):
        """Test basic command registration with decorator."""
        @command(name="test.basic", description="Basic command")
        class BasicCommand(BaseCommand):
            def get_click_command(self):
                @click.command()
                def cmd():
                    click.echo("Basic")
                return cmd
        
        # Verify registration
        assert "test.basic" in command_registry._commands
        meta = command_registry.get_command("test.basic")
        assert meta.name == "test.basic"
        assert meta.description == "Basic command"
        assert meta.command_class == BasicCommand
        assert meta.scope == CommandScope.BOTH  # Default
    
    def test_command_with_custom_scope(self):
        """Test command with custom scope."""
        @command(
            name="test.cli_only",
            description="CLI only",
            scope=CommandScope.CLI
        )
        class CliCommand(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        meta = command_registry.get_command("test.cli_only")
        assert meta.scope == CommandScope.CLI
    
    def test_command_with_aliases(self):
        """Test command registration with aliases."""
        @command(
            name="test.aliases",
            description="Command with aliases",
            aliases=["ta", "test-a", "testa"]
        )
        class AliasCommand(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        # Check main command
        meta = command_registry.get_command("test.aliases")
        assert meta.aliases == ["ta", "test-a", "testa"]
        
        # Check alias registration
        assert command_registry._aliases["ta"] == "test.aliases"
        assert command_registry._aliases["test-a"] == "test.aliases"
        assert command_registry._aliases["testa"] == "test.aliases"
    
    def test_command_metadata_storage(self):
        """Test that metadata is stored on the class."""
        @command(name="test.meta", description="Metadata test")
        class MetaCommand(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        # Check metadata on class
        assert hasattr(MetaCommand, '_command_metadata')
        assert MetaCommand._command_metadata.name == "test.meta"
    
    def test_duplicate_command_registration(self):
        """Test registering duplicate commands."""
        @command(name="test.dup", description="First")
        class FirstCommand(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        @command(name="test.dup", description="Second")
        class SecondCommand(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        # Second should overwrite first
        meta = command_registry.get_command("test.dup")
        assert meta.description == "Second"
        assert meta.command_class == SecondCommand


class TestReplCommandDecorator:
    """Test the @repl_command decorator."""
    
    def setup_method(self):
        """Clear registry before each test."""
        command_registry._commands.clear()
        command_registry._aliases.clear()
    
    def test_repl_command_registration(self):
        """Test REPL command registration."""
        @repl_command(
            name="test_repl",
            description="Test REPL command",
            aliases=["tr"]
        )
        def test_repl_func(args, context, executor):
            return f"REPL: {' '.join(args)}"
        
        # Verify registration
        meta = command_registry.get_command("test_repl")
        assert meta.name == "test_repl"
        assert meta.description == "Test REPL command"
        assert meta.scope == CommandScope.REPL
        assert meta.aliases == ["tr"]
        
        # For REPL commands, the function itself has the metadata
        assert hasattr(test_repl_func, '_command_metadata')
        assert test_repl_func._command_metadata == meta
        
        # Check alias
        assert command_registry._aliases["tr"] == "test_repl"
    
    def test_repl_command_metadata_on_function(self):
        """Test metadata storage on function."""
        @repl_command(name="meta_repl", description="Meta test")
        def meta_func(args, context, executor):
            return "Meta"
        
        assert hasattr(meta_func, '_command_metadata')
        assert meta_func._command_metadata.name == "meta_repl"
    
    def test_repl_command_execution(self):
        """Test REPL command can be executed."""
        @repl_command(name="exec_repl", description="Exec test")
        def exec_func(args, context, executor):
            return f"Args: {args}, Context: {context is not None}"
        
        # Test execution
        result = exec_func(["arg1", "arg2"], None, None)
        assert result == "Args: ['arg1', 'arg2'], Context: False"


class TestContextCommandDecorator:
    """Test the @context_command decorator."""
    
    def setup_method(self):
        """Clear registry before each test."""
        command_registry._commands.clear()
        command_registry._context_commands.clear()
    
    def test_context_command_registration(self):
        """Test context-aware command registration."""
        @context_command(
            name="gateway.test",
            description="Gateway command",
            context_types=[ContextType.GATEWAY]
        )
        class GatewayCommand(ContextAwareCommand):
            def get_click_command(self):
                @click.command()
                def cmd():
                    click.echo("Gateway")
                return cmd
            
            def get_context_args(self):
                return {"gateway": "test-gw"}
        
        # Check registration
        meta = command_registry.get_command("gateway.test")
        assert meta.name == "gateway.test"
        assert meta.context_types == [ContextType.GATEWAY]
        assert issubclass(meta.command_class, ContextAwareCommand)
        
        # Check context registration
        gateway_cmds = command_registry.get_commands_for_context(ContextType.GATEWAY)
        assert any(cmd.name == "gateway.test" for cmd in gateway_cmds)
    
    def test_context_command_with_aliases(self):
        """Test context command with aliases."""
        @context_command(
            name="client.ctx",
            description="Client context",
            context_types=[ContextType.CLIENT],
            aliases=["cc", "client-ctx"]
        )
        class ClientCommand(ContextAwareCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
            
            def get_context_args(self):
                return {}
        
        # Check aliases
        assert command_registry._aliases["cc"] == "client.ctx"
        assert command_registry._aliases["client-ctx"] == "client.ctx"
    
    def test_multiple_context_types(self):
        """Test command with multiple context types."""
        @context_command(
            name="multi.ctx",
            description="Multi context",
            context_types=[ContextType.SITE, ContextType.GATEWAY]
        )
        class MultiCommand(ContextAwareCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
            
            def get_context_args(self):
                return {}
        
        # Should be in both contexts
        site_cmds = command_registry.get_commands_for_context(ContextType.SITE)
        gateway_cmds = command_registry.get_commands_for_context(ContextType.GATEWAY)
        
        assert any(cmd.name == "multi.ctx" for cmd in site_cmds)
        assert any(cmd.name == "multi.ctx" for cmd in gateway_cmds)


class TestClickCommandAdapter:
    """Test the click_command_adapter function."""
    
    def setup_method(self):
        """Clear registry before each test."""
        command_registry._commands.clear()
    
    def test_adapt_existing_click_command(self):
        """Test adapting an existing click command."""
        # Create a click command
        @click.command()
        @click.option("--test", help="Test option")
        def existing_cmd(test):
            """Existing command help."""
            click.echo(f"Test: {test}")
        
        # Adapt it
        click_command_adapter(
            name="adapted.cmd",
            click_cmd=existing_cmd,
            scope=CommandScope.CLI
        )
        
        # Verify registration
        meta = command_registry.get_command("adapted.cmd")
        assert meta.name == "adapted.cmd"
        assert meta.description == "Existing command help."
        assert meta.scope == CommandScope.CLI
        assert meta.click_command == existing_cmd
        
        # Get instance and verify it returns the original command
        instance = command_registry.get_command_instance("adapted.cmd")
        assert instance.get_click_command() == existing_cmd
    
    def test_adapter_with_context_and_auto_inject(self):
        """Test adapter with context types and auto injection."""
        @click.command()
        def ctx_cmd():
            """Context command."""
        
        click_command_adapter(
            name="ctx.adapted",
            click_cmd=ctx_cmd,
            scope=CommandScope.BOTH,
            context_types=[ContextType.GATEWAY],
            auto_inject={"gateway": "current_gateway"}
        )
        
        meta = command_registry.get_command("ctx.adapted")
        assert meta.context_types == [ContextType.GATEWAY]
        assert meta.auto_inject_args == {"gateway": "current_gateway"}
        
        # Check context registration
        gateway_cmds = command_registry.get_commands_for_context(ContextType.GATEWAY)
        assert any(cmd.name == "ctx.adapted" for cmd in gateway_cmds)


class TestDecoratorEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Clear registry before each test."""
        command_registry._commands.clear()
        command_registry._aliases.clear()
    
    def test_empty_name_raises_error(self):
        """Test that empty name is handled."""
        with pytest.raises(ValueError, match="Command name cannot be empty"):
            @command(name="", description="Empty name")
            class EmptyName(BaseCommand):
                pass
    
    def test_invalid_scope_type(self):
        """Test invalid scope type."""
        # Should default to BOTH for invalid scope
        @command(name="test.invalid", description="Invalid scope", scope="invalid")
        class InvalidScope(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        meta = command_registry.get_command("test.invalid")
        # The decorator should handle this gracefully
        assert meta is not None
    
    def test_conflicting_aliases(self):
        """Test handling of conflicting aliases."""
        @command(name="test.first", description="First", aliases=["conflict"])
        class FirstCmd(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        @command(name="test.second", description="Second", aliases=["conflict"])
        class SecondCmd(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        # Second registration should overwrite the alias
        assert command_registry._aliases["conflict"] == "test.second"
    
    def test_decorator_on_non_base_command(self):
        """Test decorator on class not inheriting from BaseCommand."""
        # This should still work - decorator doesn't enforce inheritance
        @command(name="test.non_base", description="Non-base")
        class NonBaseCommand:
            def get_click_command(self):
                return click.command()(lambda: None)
        
        meta = command_registry.get_command("test.non_base")
        assert meta.command_class == NonBaseCommand
    
    def test_repl_command_with_invalid_function(self):
        """Test REPL decorator on non-callable."""
        # This would be a programming error, but test handling
        try:
            @repl_command(name="invalid", description="Invalid")
            class NotAFunction:
                pass
            # If no error, check registration
            meta = command_registry.get_command("invalid")
            assert meta is not None
        except TypeError:
            # Expected if decorator validates
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
