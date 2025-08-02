"""Comprehensive tests for command loader."""

import importlib
import types
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import click
import pytest

from aceiot_models_cli.commands.base import BaseCommand, CommandScope, command_registry
from aceiot_models_cli.commands.decorators import command, repl_command
from aceiot_models_cli.commands.loader import CommandLoader, command_loader


class TestCommandLoader:
    """Test CommandLoader functionality."""
    
    def setup_method(self):
        """Create fresh loader and clear registry."""
        self.loader = CommandLoader()
        command_registry._commands.clear()
        command_registry._aliases.clear()
        command_registry._context_commands.clear()
        # Clear the loaded modules tracker
        self.loader._loaded_modules.clear()
    
    def test_loader_singleton(self):
        """Test that command_loader is a singleton."""
        from aceiot_models_cli.commands.loader import command_loader as loader2
        assert command_loader is loader2
    
    def test_load_module_with_decorated_class(self):
        """Test loading a module with decorated classes."""
        # Clear registry first
        command_registry._commands.clear()
        
        # Create a test module
        test_module = types.ModuleType("test_module")
        
        # Add decorated class - this registers immediately
        @command(name="discovered.cmd", description="Discovered command")
        class DiscoveredCommand(BaseCommand):
            def get_click_command(self):
                import click
                return click.command()(lambda: None)
        
        # Add non-decorated class
        class RegularClass:
            pass
        
        # Add function
        def some_function():
            pass
        
        test_module.DiscoveredCommand = DiscoveredCommand
        test_module.RegularClass = RegularClass
        test_module.some_function = some_function
        
        # Command is already registered by decorator
        assert "discovered.cmd" in command_registry._commands
        
        # Load from module - counts decorated classes
        count = self.loader.load_commands_from_module(test_module)
        
        # Should count the decorated class
        assert count == 1
    
    def test_load_module_with_repl_function(self):
        """Test loading module with REPL command functions."""
        test_module = types.ModuleType("test_functions")
        
        # Add decorated function
        @repl_command(name="discovered.func", description="Discovered function")
        def discovered_func(args, context, executor):
            return "discovered"
        
        # Add regular function
        def regular_func():
            pass
        
        test_module.discovered_func = discovered_func
        test_module.regular_func = regular_func
        
        # Clear registry
        command_registry._commands.clear()
        
        # Note: Current loader only handles classes, not functions
        # This is a limitation of the current implementation
        count = self.loader.load_commands_from_module(test_module)
        
        # Will be 0 because loader only looks for BaseCommand subclasses
        assert count == 0
    
    def test_load_module_multiple_commands(self):
        """Test loading module with multiple commands."""
        # Clear registry first
        command_registry._commands.clear()
        
        test_module = types.ModuleType("test_multi")
        
        @command(name="multi.cmd1", description="Command 1")
        class Command1(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        @command(name="multi.cmd2", description="Command 2")
        class Command2(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        test_module.Command1 = Command1
        test_module.Command2 = Command2
        
        # Commands are already registered by decorators
        assert "multi.cmd1" in command_registry._commands
        assert "multi.cmd2" in command_registry._commands
        
        # Load - counts decorated classes
        count = self.loader.load_commands_from_module(test_module)
        
        assert count == 2
    
    def test_load_module_already_loaded(self):
        """Test that modules can be loaded multiple times."""
        # Clear registry
        command_registry._commands.clear()
        
        test_module = types.ModuleType("test_already_loaded")
        
        @command(name="loaded.cmd", description="Loaded command")
        class LoadedCommand(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        test_module.LoadedCommand = LoadedCommand
        
        # Load first time
        count1 = self.loader.load_commands_from_module(test_module)
        assert count1 == 1
        
        # Load second time (counts same command again)
        count2 = self.loader.load_commands_from_module(test_module)
        assert count2 == 1  # Still counts the command
        
        # But only one command in registry (decorator only registers once)
        assert len([k for k in command_registry._commands.keys() if k == "loaded.cmd"]) == 1
    
    def test_load_commands_from_package(self):
        """Test loading commands from a package name."""
        # Clear registry first
        command_registry._commands.clear()
        
        # Create a mock module
        mock_module = MagicMock()
        mock_module.__name__ = "test_package"
        
        @command(name="pkg.cmd", description="Package command")
        class PkgCommand(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        # Mock attributes
        mock_module.PkgCommand = PkgCommand
        
        # Command is already registered
        assert "pkg.cmd" in command_registry._commands
        
        # Mock inspect.getmembers to return our command
        with patch('inspect.getmembers', return_value=[('PkgCommand', PkgCommand)]):
            with patch('importlib.import_module', return_value=mock_module):
                # Load
                count = self.loader.load_commands_from_package("test_package")
                
                # Should count the command
                assert count == 1
    
    def test_load_commands_from_package_import_error(self):
        """Test handling import errors gracefully."""
        with patch('importlib.import_module', side_effect=ImportError("No module")):
            # Should raise with helpful message
            with pytest.raises(ImportError, match="Failed to import package"):
                self.loader.load_commands_from_package("nonexistent.package")
    
    def test_load_commands_from_directory(self):
        """Test loading commands from a directory."""
        # Create a temporary directory structure
        import os
        import sys
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create __init__.py
            init_file = Path(tmpdir) / "__init__.py"
            init_file.write_text("")
            
            # Create a command file
            cmd_file = Path(tmpdir) / "commands.py"
            cmd_file.write_text("""
from aceiot_models_cli.commands.base import BaseCommand
from aceiot_models_cli.commands.decorators import command
import click

@command(name="dir.cmd", description="Directory command")
class DirCommand(BaseCommand):
    def get_click_command(self):
        return click.command()(lambda: None)
""")
            
            # Clear registry
            command_registry._commands.clear()
            
            # Add to sys.path temporarily
            sys.path.insert(0, str(Path(tmpdir).parent))
            try:
                # Load from directory - uses importlib to load files
                count = self.loader.load_commands_from_directory(Path(tmpdir))
                
                # The implementation does execute the module, so decorators run
                assert count == 1  # Found one decorated command
                assert "dir.cmd" in command_registry._commands
            finally:
                sys.path.pop(0)
    
    def test_register_click_group(self):
        """Test registering commands in a click group."""
        # Clear registry
        command_registry._commands.clear()
        
        # Create a click group
        group = click.Group(name="test")
        
        # Create some commands in registry
        @command(name="test.cmd1", description="Test command 1", scope=CommandScope.CLI)
        class TestCmd1(BaseCommand):
            def get_click_command(self):
                @click.command("cmd1")
                def cmd():
                    """Command 1"""
                    click.echo("cmd1")
                return cmd
        
        @command(name="test.cmd2", description="Test command 2", scope=CommandScope.REPL)
        class TestCmd2(BaseCommand):
            def get_click_command(self):
                @click.command("cmd2")
                def cmd():
                    """Command 2"""
                    click.echo("cmd2")
                return cmd
        
        # Commands are already registered by decorators
        assert "test.cmd1" in command_registry._commands
        assert "test.cmd2" in command_registry._commands
        
        # Actually the current register_click_group implementation
        # processes existing click group commands and registers them,
        # not the other way around. Let's test that:
        
        # Add some existing click commands to the group
        @click.command("existing")
        def existing_cmd():
            """Existing command"""
            click.echo("existing")
        
        group.add_command(existing_cmd)
        
        # Register click group
        self.loader.register_click_group(group, prefix="test.")
        
        # This should have registered the existing command
        assert "test.existing" in command_registry._commands
    
    def test_build_click_group(self):
        """Test building a new click group from registry."""
        # Clear registry first
        command_registry._commands.clear()
        
        # Create commands
        @command(name="built.cmd", description="Built command", scope=CommandScope.CLI)
        class BuiltCmd(BaseCommand):
            def get_click_command(self):
                @click.command("cmd")  # Last part of name
                def cmd():
                    """Built command"""
                    click.echo("built")
                return cmd
        
        # Command is already registered by decorator
        assert "built.cmd" in command_registry._commands
        
        # Build group
        group = self.loader.build_click_group("mygroup")
        
        # Should have created a subgroup "built" with command "cmd"
        assert group.name == "mygroup"
        assert "built" in group.commands
        assert isinstance(group.commands["built"], click.Group)
    
    def test_load_module_without_name_attribute(self):
        """Test loading module without __name__ attribute."""
        # Clear registry
        command_registry._commands.clear()
        
        test_module = types.ModuleType("test_no_name")
        # Remove __name__ to simulate edge case
        delattr(test_module, "__name__")
        
        @command(name="noname.cmd", description="No name command")
        class NoNameCommand(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        test_module.NoNameCommand = NoNameCommand
        
        # Should handle gracefully
        count = self.loader.load_commands_from_module(test_module)
        
        # Should still count the command
        assert count == 1
    
    def test_command_without_metadata(self):
        """Test that classes without metadata are skipped."""
        test_module = types.ModuleType("test_no_meta")
        
        # Command without decorator (no metadata)
        class NoMetaCommand(BaseCommand):
            def get_click_command(self):
                return click.command()(lambda: None)
        
        test_module.NoMetaCommand = NoMetaCommand
        
        # Clear registry
        command_registry._commands.clear()
        
        # Load
        count = self.loader.load_commands_from_module(test_module)
        
        # Should not load anything
        assert count == 0
        assert len(command_registry._commands) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
