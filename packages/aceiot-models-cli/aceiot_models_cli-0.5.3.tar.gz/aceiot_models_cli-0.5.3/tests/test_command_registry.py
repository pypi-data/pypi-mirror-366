"""Comprehensive tests for command registry."""

from unittest.mock import Mock, patch

import click
import pytest

from aceiot_models_cli.commands.base import (
    BaseCommand,
    CommandMetadata,
    CommandRegistry,
    CommandScope,
    ContextAwareCommand,
    command_registry,
)
from aceiot_models_cli.repl.context import ContextType, ReplContext


class TestCommandRegistry:
    """Test CommandRegistry class functionality."""
    
    def setup_method(self):
        """Create fresh registry for each test."""
        self.registry = CommandRegistry()
    
    def test_register_command(self):
        """Test basic command registration."""
        meta = CommandMetadata(
            name="test.cmd",
            description="Test command",
            scope=CommandScope.CLI,
            command_class=BaseCommand
        )
        
        self.registry.register(meta)
        
        # Check it's registered
        assert "test.cmd" in self.registry._commands
        assert self.registry._commands["test.cmd"] == meta
    
    def test_register_with_aliases(self):
        """Test registering command with aliases."""
        meta = CommandMetadata(
            name="test.alias",
            description="Aliased command",
            scope=CommandScope.BOTH,
            aliases=["ta", "test-a"],
            command_class=BaseCommand
        )
        
        self.registry.register(meta)
        
        # Check aliases are registered
        assert self.registry._aliases["ta"] == "test.alias"
        assert self.registry._aliases["test-a"] == "test.alias"
    
    def test_register_context_command(self):
        """Test registering context-aware command."""
        meta = CommandMetadata(
            name="gateway.cmd",
            description="Gateway command",
            scope=CommandScope.CONTEXT,
            context_types=[ContextType.GATEWAY],
            command_class=ContextAwareCommand
        )
        
        self.registry.register(meta)
        
        # Check context registration
        assert ContextType.GATEWAY in self.registry._context_commands
        assert "gateway.cmd" in self.registry._context_commands[ContextType.GATEWAY]
    
    def test_register_multi_context_command(self):
        """Test command with multiple contexts."""
        meta = CommandMetadata(
            name="multi.cmd",
            description="Multi-context command",
            scope=CommandScope.CONTEXT,
            context_types=[ContextType.SITE, ContextType.GATEWAY],
            command_class=ContextAwareCommand
        )
        
        self.registry.register(meta)
        
        # Should be in both contexts
        assert "multi.cmd" in self.registry._context_commands[ContextType.SITE]
        assert "multi.cmd" in self.registry._context_commands[ContextType.GATEWAY]
    
    def test_get_command(self):
        """Test retrieving commands."""
        meta = CommandMetadata(
            name="get.test",
            description="Get test",
            scope=CommandScope.CLI,
            command_class=BaseCommand
        )
        
        self.registry.register(meta)
        
        # Get by name
        retrieved = self.registry.get_command("get.test")
        assert retrieved == meta
        
        # Non-existent returns None
        assert self.registry.get_command("nonexistent") is None
    
    def test_get_command_by_alias(self):
        """Test retrieving command by alias."""
        meta = CommandMetadata(
            name="alias.test",
            description="Alias test",
            scope=CommandScope.CLI,
            aliases=["at"],
            command_class=BaseCommand
        )
        
        self.registry.register(meta)
        
        # Get by alias
        retrieved = self.registry.get_command("at")
        assert retrieved == meta
        assert retrieved.name == "alias.test"
    
    def test_get_command_instance_without_context(self):
        """Test getting command instance without context."""
        class TestCommand(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        meta = CommandMetadata(
            name="instance.test",
            description="Instance test",
            scope=CommandScope.CLI,
            command_class=TestCommand
        )
        
        self.registry.register(meta)
        
        # Get instance
        instance = self.registry.get_command_instance("instance.test")
        assert instance is not None
        assert isinstance(instance, TestCommand)
        assert hasattr(instance, 'metadata')
        assert instance.metadata == meta
    
    def test_get_command_instance_with_context(self):
        """Test getting context-aware command instance."""
        class ContextCommand(ContextAwareCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
            
            def get_context_args(self):
                return {"gateway": self.context.current_gateway}
        
        meta = CommandMetadata(
            name="ctx.instance",
            description="Context instance",
            scope=CommandScope.CONTEXT,
            context_types=[ContextType.GATEWAY],
            command_class=ContextCommand
        )
        
        self.registry.register(meta)
        
        # Create context
        context = ReplContext()
        context.enter_context(ContextType.GATEWAY, "test-gw")
        
        # Get instance with context
        instance = self.registry.get_command_instance("ctx.instance", context)
        assert instance is not None
        assert isinstance(instance, ContextCommand)
        assert instance.context == context
        
        # Test context args work
        ctx_args = instance.get_context_args()
        assert ctx_args["gateway"] == "test-gw"
    
    def test_get_command_instance_non_class(self):
        """Test getting instance when command is not a class."""
        # For REPL commands that are functions
        def repl_func(args, context, executor):
            return "REPL"
        
        meta = CommandMetadata(
            name="func.cmd",
            description="Function command",
            scope=CommandScope.REPL,
            command_class=repl_func  # Function, not class
        )
        
        self.registry.register(meta)
        
        # Should return None for non-class
        instance = self.registry.get_command_instance("func.cmd")
        assert instance is None
    
    def test_get_commands_for_context(self):
        """Test getting commands for specific context."""
        # Register some context commands
        gateway_meta = CommandMetadata(
            name="gw.cmd1",
            description="Gateway 1",
            scope=CommandScope.CONTEXT,
            context_types=[ContextType.GATEWAY],
            command_class=ContextAwareCommand
        )
        
        site_meta = CommandMetadata(
            name="site.cmd1",
            description="Site 1",
            scope=CommandScope.CONTEXT,
            context_types=[ContextType.SITE],
            command_class=ContextAwareCommand
        )
        
        multi_meta = CommandMetadata(
            name="multi.cmd1",
            description="Multi 1",
            scope=CommandScope.CONTEXT,
            context_types=[ContextType.SITE, ContextType.GATEWAY],
            command_class=ContextAwareCommand
        )
        
        self.registry.register(gateway_meta)
        self.registry.register(site_meta)
        self.registry.register(multi_meta)
        
        # Get gateway commands
        gateway_cmds = self.registry.get_commands_for_context(ContextType.GATEWAY)
        assert len(gateway_cmds) == 2
        assert any(cmd.name == "gw.cmd1" for cmd in gateway_cmds)
        assert any(cmd.name == "multi.cmd1" for cmd in gateway_cmds)
        
        # Get site commands
        site_cmds = self.registry.get_commands_for_context(ContextType.SITE)
        assert len(site_cmds) == 2
        assert any(cmd.name == "site.cmd1" for cmd in site_cmds)
        assert any(cmd.name == "multi.cmd1" for cmd in site_cmds)
        
        # Get client commands (none registered)
        client_cmds = self.registry.get_commands_for_context(ContextType.CLIENT)
        assert len(client_cmds) == 0
    
    def test_get_all_commands(self):
        """Test getting all commands with optional scope filter."""
        # Register commands with different scopes
        cli_meta = CommandMetadata(
            name="cli.cmd",
            description="CLI command",
            scope=CommandScope.CLI,
            command_class=BaseCommand
        )
        
        repl_meta = CommandMetadata(
            name="repl.cmd",
            description="REPL command",
            scope=CommandScope.REPL,
            command_class=BaseCommand
        )
        
        both_meta = CommandMetadata(
            name="both.cmd",
            description="Both command",
            scope=CommandScope.BOTH,
            command_class=BaseCommand
        )
        
        self.registry.register(cli_meta)
        self.registry.register(repl_meta)
        self.registry.register(both_meta)
        
        # Get all commands
        all_cmds = self.registry.get_all_commands()
        assert len(all_cmds) == 3
        
        # Get CLI commands (includes BOTH)
        cli_cmds = self.registry.get_all_commands(scope=CommandScope.CLI)
        assert len(cli_cmds) == 2
        assert any(cmd.name == "cli.cmd" for cmd in cli_cmds)
        assert any(cmd.name == "both.cmd" for cmd in cli_cmds)
        
        # Get REPL commands (includes BOTH)
        repl_cmds = self.registry.get_all_commands(scope=CommandScope.REPL)
        assert len(repl_cmds) == 2
        assert any(cmd.name == "repl.cmd" for cmd in repl_cmds)
        assert any(cmd.name == "both.cmd" for cmd in repl_cmds)
        
        # Get BOTH scope only
        both_cmds = self.registry.get_all_commands(scope=CommandScope.BOTH)
        assert len(both_cmds) == 1
        assert both_cmds[0].name == "both.cmd"
    
    def test_duplicate_registration(self):
        """Test that duplicate registrations overwrite."""
        meta1 = CommandMetadata(
            name="dup.cmd",
            description="First version",
            scope=CommandScope.CLI,
            command_class=BaseCommand
        )
        
        meta2 = CommandMetadata(
            name="dup.cmd",
            description="Second version",
            scope=CommandScope.REPL,
            command_class=BaseCommand
        )
        
        self.registry.register(meta1)
        self.registry.register(meta2)
        
        # Second should overwrite
        retrieved = self.registry.get_command("dup.cmd")
        assert retrieved.description == "Second version"
        assert retrieved.scope == CommandScope.REPL
    
    def test_alias_conflict_resolution(self):
        """Test alias conflicts are handled."""
        meta1 = CommandMetadata(
            name="cmd1",
            description="Command 1",
            scope=CommandScope.CLI,
            aliases=["shared"],
            command_class=BaseCommand
        )
        
        meta2 = CommandMetadata(
            name="cmd2",
            description="Command 2",
            scope=CommandScope.CLI,
            aliases=["shared"],
            command_class=BaseCommand
        )
        
        self.registry.register(meta1)
        self.registry.register(meta2)
        
        # Second registration should take the alias
        assert self.registry._aliases["shared"] == "cmd2"
        
        # Getting by alias returns second command
        cmd = self.registry.get_command("shared")
        assert cmd.name == "cmd2"


class TestGlobalRegistry:
    """Test the global command_registry instance."""
    
    def setup_method(self):
        """Clear global registry before each test."""
        command_registry._commands.clear()
        command_registry._aliases.clear()
        command_registry._context_commands.clear()
    
    def test_global_registry_is_singleton(self):
        """Test that command_registry is a singleton."""
        # Import again to check it's the same instance
        from aceiot_models_cli.commands.base import command_registry as registry2
        
        assert command_registry is registry2
    
    def test_global_registry_operations(self):
        """Test operations on global registry."""
        meta = CommandMetadata(
            name="global.test",
            description="Global test",
            scope=CommandScope.CLI,
            command_class=BaseCommand
        )
        
        command_registry.register(meta)
        
        # Should be retrievable
        retrieved = command_registry.get_command("global.test")
        assert retrieved == meta
        
        # Should appear in all commands
        all_cmds = command_registry.get_all_commands()
        assert any(cmd.name == "global.test" for cmd in all_cmds)


class TestCommandMetadata:
    """Test CommandMetadata dataclass."""
    
    def test_metadata_creation(self):
        """Test creating metadata with various options."""
        meta = CommandMetadata(
            name="meta.test",
            description="Metadata test",
            scope=CommandScope.BOTH,
            context_types=[ContextType.GATEWAY],
            aliases=["mt", "meta-t"],
            parent_command="parent",
            requires_context=True,
            auto_inject_args={"gateway": "current_gateway"},
            command_class=BaseCommand,
            click_command=None
        )
        
        assert meta.name == "meta.test"
        assert meta.description == "Metadata test"
        assert meta.scope == CommandScope.BOTH
        assert meta.context_types == [ContextType.GATEWAY]
        assert meta.aliases == ["mt", "meta-t"]
        assert meta.parent_command == "parent"
        assert meta.requires_context is True
        assert meta.auto_inject_args == {"gateway": "current_gateway"}
        assert meta.command_class == BaseCommand
        assert meta.click_command is None
    
    def test_metadata_defaults(self):
        """Test metadata default values."""
        meta = CommandMetadata(
            name="default.test",
            description="Default test",
            scope=CommandScope.CLI,
            command_class=BaseCommand
        )
        
        # Check defaults
        assert meta.context_types == []
        assert meta.aliases == []
        assert meta.parent_command is None
        assert meta.requires_context is False
        assert meta.auto_inject_args == {}
        assert meta.click_command is None
    
    def test_metadata_equality(self):
        """Test metadata equality comparison."""
        meta1 = CommandMetadata(
            name="eq.test",
            description="Equality test",
            scope=CommandScope.CLI,
            command_class=BaseCommand
        )
        
        meta2 = CommandMetadata(
            name="eq.test",
            description="Equality test",
            scope=CommandScope.CLI,
            command_class=BaseCommand
        )
        
        meta3 = CommandMetadata(
            name="different",
            description="Different",
            scope=CommandScope.CLI,
            command_class=BaseCommand
        )
        
        assert meta1 == meta2
        assert meta1 != meta3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
