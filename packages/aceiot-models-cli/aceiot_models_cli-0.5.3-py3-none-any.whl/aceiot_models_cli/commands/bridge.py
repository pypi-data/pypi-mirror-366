"""Bridge to integrate new command architecture with existing CLI."""

import click

from .loader import command_loader


def replace_command_group(cli: click.Group, group_name: str) -> bool:
    """Replace a command group in the CLI with the dynamic version."""
    # Load commands from the appropriate module
    module_map = {
        "clients": "aceiot_models_cli.commands.client",
        "sites": "aceiot_models_cli.commands.site",
        "gateways": "aceiot_models_cli.commands.gateway",
        "points": "aceiot_models_cli.commands.point",
        "volttron": "aceiot_models_cli.commands.volttron_cmds",
    }

    if group_name in module_map:
        try:
            # Load the commands
            module = __import__(module_map[group_name], fromlist=[""])
            command_loader.load_commands_from_module(module)

            # Build dynamic CLI
            dynamic_cli = command_loader.build_click_group()

            # Replace the group
            if group_name in dynamic_cli.commands:
                cli.commands[group_name] = dynamic_cli.commands[group_name]
                return True
        except ImportError:
            # Module doesn't exist yet, skip
            pass

    return False


def integrate_new_commands(cli: click.Group) -> None:
    """Integrate all available new command modules with the CLI."""
    groups_to_replace = ["clients", "sites", "gateways", "points", "volttron"]

    for group in groups_to_replace:
        replace_command_group(cli, group)
