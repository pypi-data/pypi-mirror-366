"""Base classes for command architecture."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import click
from aceiot_models.api import APIClient, APIError

from ..repl.context import ContextType, ReplContext


class CommandScope(Enum):
    """Scope where command is available."""
    CLI = "cli"          # Available in CLI mode
    REPL = "repl"        # Available in REPL mode
    BOTH = "both"        # Available in both modes
    CONTEXT = "context"  # Only available in specific context


@dataclass
class CommandMetadata:
    """Metadata for registered commands."""
    name: str
    description: str
    scope: CommandScope = CommandScope.BOTH
    context_types: list[ContextType] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    parent_command: str | None = None

    # For context-aware commands
    requires_context: bool = False
    auto_inject_args: dict[str, str] = field(default_factory=dict)  # param_name -> context_attr

    # Command implementation
    command_class: type["BaseCommand"] | None = None
    click_command: click.Command | None = None


class BaseCommand(ABC):
    """Base class for all commands."""

    def __init__(self, api_client: APIClient | None = None):
        self.api_client = api_client
        self._metadata: CommandMetadata | None = None

    @property
    def metadata(self) -> CommandMetadata:
        """Get command metadata."""
        if self._metadata is None:
            raise ValueError(f"Command {self.__class__.__name__} not registered")
        return self._metadata

    @metadata.setter
    def metadata(self, value: CommandMetadata) -> None:
        """Set command metadata."""
        self._metadata = value

    @abstractmethod
    def get_click_command(self) -> click.Command:
        """Return the click command implementation."""

    def get_api_error_detail(self, error: APIError) -> str:
        """Extract detailed error message from APIError."""
        if error.response_data and isinstance(error.response_data, dict):
            return error.response_data.get("detail", str(error))
        return str(error)

    def require_api_client(self, ctx: click.Context) -> APIClient:
        """Ensure API client is available, exit if not."""
        if self.api_client:
            return self.api_client

        if "client" not in ctx.obj or ctx.obj["client"] is None:
            from ..formatters import print_error
            print_error("API key is required. Set ACEIOT_API_KEY or use --api-key")
            ctx.exit(1)

        self.api_client = ctx.obj["client"]
        return self.api_client


class ContextAwareCommand(BaseCommand):
    """Base class for commands that are context-aware."""

    def __init__(self, context: ReplContext | None = None, **kwargs):
        super().__init__(**kwargs)
        self.context = context

    def get_context_args(self) -> dict[str, Any]:
        """Get arguments from current context."""
        if not self.context:
            return {}
        return self.context.get_context_args()

    def inject_context_args(self, ctx: click.Context, **kwargs) -> dict[str, Any]:
        """Inject context arguments into command kwargs."""
        context_args = self.get_context_args()

        # Apply auto-injection rules from metadata
        if self.metadata and self.metadata.auto_inject_args:
            for param_name, context_attr in self.metadata.auto_inject_args.items():
                if context_attr in context_args and param_name not in kwargs:
                    kwargs[param_name] = context_args[context_attr]

        return kwargs

    @property
    def current_client(self) -> str | None:
        """Get current client from context."""
        return self.context.current_client if self.context else None

    @property
    def current_site(self) -> str | None:
        """Get current site from context."""
        return self.context.current_site if self.context else None

    @property
    def current_gateway(self) -> str | None:
        """Get current gateway from context."""
        return self.context.current_gateway if self.context else None


class CommandRegistry:
    """Registry for dynamic command management."""

    def __init__(self):
        self._commands: dict[str, CommandMetadata] = {}
        self._aliases: dict[str, str] = {}  # alias -> command_name
        self._context_commands: dict[ContextType, list[str]] = {}
        self._command_instances: dict[str, BaseCommand] = {}

    def register(self, metadata: CommandMetadata) -> None:
        """Register a command."""
        # Store metadata
        self._commands[metadata.name] = metadata

        # Register aliases
        for alias in metadata.aliases:
            self._aliases[alias] = metadata.name

        # Register context-specific commands
        for context_type in metadata.context_types:
            if context_type not in self._context_commands:
                self._context_commands[context_type] = []
            self._context_commands[context_type].append(metadata.name)

    def get_command(self, name: str) -> CommandMetadata | None:
        """Get command metadata by name or alias."""
        # Check direct name
        if name in self._commands:
            return self._commands[name]

        # Check aliases
        if name in self._aliases:
            return self._commands[self._aliases[name]]

        return None

    def get_command_instance(self, name: str, context: ReplContext | None = None) -> BaseCommand | None:
        """Get or create command instance."""
        metadata = self.get_command(name)
        if not metadata or not metadata.command_class:
            return None

        # Check if it's actually a class (not a function)
        import inspect
        if not inspect.isclass(metadata.command_class):
            return None  # Can't instantiate functions

        # Create instance if needed
        cache_key = f"{name}_{id(context)}" if context else name
        if cache_key not in self._command_instances:
            if issubclass(metadata.command_class, ContextAwareCommand):
                instance = metadata.command_class(context=context)
            else:
                instance = metadata.command_class()

            instance.metadata = metadata
            self._command_instances[cache_key] = instance

        return self._command_instances[cache_key]

    def get_commands_for_context(self, context_type: ContextType) -> list[CommandMetadata]:
        """Get all commands available in a specific context."""
        command_names = self._context_commands.get(context_type, [])
        return [self._commands[name] for name in command_names if name in self._commands]

    def get_all_commands(self, scope: CommandScope | None = None) -> list[CommandMetadata]:
        """Get all registered commands, optionally filtered by scope."""
        commands = list(self._commands.values())

        if scope:
            commands = [cmd for cmd in commands if cmd.scope in (scope, CommandScope.BOTH)]

        return commands

    def build_click_group(self, scope: CommandScope = CommandScope.CLI) -> click.Group:
        """Build a click group with all registered commands for a given scope."""
        # This would dynamically build the CLI structure from registered commands
        # Implementation would create groups and add commands based on metadata
        # Return a new empty group for now
        return click.Group()


# Global registry instance
command_registry = CommandRegistry()
