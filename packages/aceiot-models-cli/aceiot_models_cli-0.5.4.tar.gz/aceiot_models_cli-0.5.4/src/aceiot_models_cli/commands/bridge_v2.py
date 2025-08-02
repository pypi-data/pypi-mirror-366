"""Enhanced bridge to integrate new command architecture with existing CLI."""

import click

from .base import CommandScope, command_registry
from .loader import command_loader


def replace_or_add_command(group: click.Group, cmd_name: str, new_cmd: click.Command) -> None:
    """Replace or add a command in a group."""
    # Remove old command if it exists
    if cmd_name in group.commands:
        del group.commands[cmd_name]

    # Add new command
    group.add_command(new_cmd)


def integrate_commands_into_group(cli_group: click.Group, group_name: str) -> None:
    """Integrate new commands into an existing CLI group."""
    # Load commands from the appropriate module
    module_map = {
        "clients": "aceiot_models_cli.commands.client",
        "sites": "aceiot_models_cli.commands.site",
        "gateways": "aceiot_models_cli.commands.gateway",
        "points": "aceiot_models_cli.commands.point",
        "volttron": "aceiot_models_cli.commands.volttron",
    }

    if group_name not in module_map:
        return

    try:
        # Load the commands
        module = __import__(module_map[group_name], fromlist=[""])
        command_loader.load_commands_from_module(module)

        # Find commands for this group
        prefix = f"{group_name}."
        for cmd_name, metadata in command_registry._commands.items():
            if cmd_name.startswith(prefix) and metadata.scope in (CommandScope.CLI, CommandScope.BOTH):
                # Extract command name (e.g., "sites.list" -> "list")
                _, cmd_short_name = cmd_name.split(".", 1)

                # Create command instance
                if metadata.command_class:
                    instance = metadata.command_class()
                    instance.metadata = metadata
                    click_cmd = instance.get_click_command()

                    # Replace or add command
                    replace_or_add_command(cli_group, cmd_short_name, click_cmd)
                elif metadata.click_command:
                    replace_or_add_command(cli_group, cmd_short_name, metadata.click_command)

    except ImportError:
        # Module doesn't exist yet, skip
        pass


def integrate_new_commands(cli: click.Group) -> None:
    """Integrate all available new command modules with the CLI."""
    # For each command group in the CLI
    for group_name, group_cmd in cli.commands.items():
        if isinstance(group_cmd, click.Group):
            integrate_commands_into_group(group_cmd, group_name)
