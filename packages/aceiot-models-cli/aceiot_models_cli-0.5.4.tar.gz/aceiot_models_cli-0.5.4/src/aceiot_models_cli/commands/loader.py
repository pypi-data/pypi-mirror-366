"""Dynamic command loader for automatic command discovery and registration."""

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Any

import click

from .base import BaseCommand, CommandRegistry, CommandScope, command_registry
from .decorators import click_command_adapter


class CommandLoader:
    """Dynamically loads and registers commands."""

    def __init__(self, registry: CommandRegistry | None = None):
        self.registry = registry or command_registry
        self._loaded_modules = set()

    def load_commands_from_module(self, module: Any) -> int:
        """Load all commands from a module."""
        count = 0

        for name, obj in inspect.getmembers(module):
            # Check if it's a command class
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseCommand)
                and obj is not BaseCommand
                and hasattr(obj, '_command_metadata')
            ):
                # Command is already registered via decorator
                count += 1

        return count

    def load_commands_from_package(self, package_name: str) -> int:
        """Load all commands from a package recursively."""
        count = 0

        try:
            package = importlib.import_module(package_name)
        except ImportError as e:
            raise ImportError(f"Failed to import package {package_name}: {e}")

        # Get package path
        if hasattr(package, '__path__'):
            package_path = package.__path__
        else:
            # Single module, not a package
            return self.load_commands_from_module(package)

        # Walk through all modules in package
        for importer, modname, ispkg in pkgutil.walk_packages(
            package_path,
            prefix=package_name + "."
        ):
            if modname in self._loaded_modules:
                continue

            try:
                module = importlib.import_module(modname)
                self._loaded_modules.add(modname)
                count += self.load_commands_from_module(module)
            except ImportError:
                # Skip modules that can't be imported
                continue

        return count

    def load_commands_from_directory(self, directory: Path) -> int:
        """Load all Python files from a directory as command modules."""
        count = 0

        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        for py_file in directory.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            # Import as module
            module_name = py_file.stem
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                count += self.load_commands_from_module(module)

        return count

    def register_click_group(self, group: click.Group, prefix: str = "") -> None:
        """Register all commands from an existing click group."""
        for name, command in group.commands.items():
            if isinstance(command, click.Group):
                # Recursively register subgroups
                self.register_click_group(command, prefix=f"{prefix}{name}.")
            else:
                # Register the command
                full_name = f"{prefix}{name}"
                click_command_adapter(
                    name=full_name,
                    click_cmd=command,
                )

    def build_click_group(self, name: str = "cli") -> click.Group:
        """Build a click group from all registered commands."""
        root_group = click.Group(name=name)

        # Track created groups
        groups = {}

        # Process all commands
        for cmd_name, metadata in self.registry._commands.items():
            # Skip context-specific commands for CLI
            if metadata.scope == CommandScope.CONTEXT:
                continue

            # Parse command path (e.g., "clients.list" -> ["clients", "list"])
            parts = cmd_name.split(".")

            # Ensure parent groups exist
            current_group = root_group
            for i, part in enumerate(parts[:-1]):
                group_path = ".".join(parts[:i+1])

                if group_path not in groups:
                    # Create new group
                    new_group = click.Group(name=part, help=f"Manage {part}")
                    current_group.add_command(new_group)
                    groups[group_path] = new_group
                    current_group = new_group
                else:
                    current_group = groups[group_path]

            # Create command instance
            if metadata.command_class:
                instance = metadata.command_class()
                instance.metadata = metadata
                click_cmd = instance.get_click_command()

                # Add to parent group
                current_group.add_command(click_cmd)
            elif metadata.click_command:
                current_group.add_command(metadata.click_command)

        return root_group


# Global loader instance
command_loader = CommandLoader()


def auto_load_commands(*packages: str) -> None:
    """Automatically load commands from specified packages."""
    for package in packages:
        try:
            count = command_loader.load_commands_from_package(package)
            print(f"Loaded {count} commands from {package}")
        except ImportError as e:
            print(f"Failed to load commands from {package}: {e}")
