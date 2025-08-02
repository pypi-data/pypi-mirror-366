"""Command execution for REPL mode using new command architecture."""

from typing import Any

import click
from aceiot_models.api import APIClient
from rich.console import Console
from rich.table import Table

from ..commands.base import CommandScope, command_registry
from ..commands.loader import command_loader
from .context import ContextType, ReplContext
from .parser import ParsedCommand
from .volttron_repl import VolttronReplHandler


class ReplCommandExecutor:
    """Executes commands in REPL mode using command registry."""

    def __init__(self, click_group: click.Group, click_ctx: click.Context) -> None:
        self.click_group = click_group
        self.click_ctx = click_ctx
        self.console = Console()
        self.volttron_handler = None  # Will be created when needed

        # Load REPL commands
        self._load_repl_commands()

    def _load_repl_commands(self) -> None:
        """Load REPL-specific commands."""
        # Load context-aware commands first
        for module_name in ['gateway', 'client', 'site', 'point']:
            try:
                module = __import__(f'aceiot_models_cli.commands.{module_name}', fromlist=[module_name])
                command_loader.load_commands_from_module(module)
            except ImportError:
                pass

        # Load REPL commands last so they take precedence for common names like "get"
        try:
            import aceiot_models_cli.commands.repl
            command_loader.load_commands_from_module(aceiot_models_cli.commands.repl)
        except ImportError:
            pass

    def execute(self, parsed_cmd: ParsedCommand, context: ReplContext) -> Any:
        """Execute a parsed command."""
        command_name = parsed_cmd.command_path[0]

        # Handle BACnet commands as REPL commands when in gateway context
        if context.current_gateway:
            bacnet_commands = ["trigger-scan", "deploy-points", "enable-bacnet", "disable-bacnet", "bacnet-status"]
            if command_name in bacnet_commands:
                # Execute as context command
                return self._execute_bacnet_in_context(parsed_cmd, context)

            # Also handle when called as gateways trigger-scan etc
            if len(parsed_cmd.command_path) >= 2 and parsed_cmd.command_path[0] == "gateways":
                bacnet_cmd = parsed_cmd.command_path[1]
                if bacnet_cmd in bacnet_commands:
                    # Already has the gateways prefix, just inject gateway name
                    if not parsed_cmd.arguments:
                        parsed_cmd.arguments = [context.current_gateway]
                    return self._execute_cli_command(parsed_cmd, context)

        # Check if it's a REPL command first
        repl_cmd = command_registry.get_command(command_name)
        if repl_cmd and repl_cmd.scope in (CommandScope.REPL, CommandScope.BOTH):
            return self._execute_repl_command(parsed_cmd, context)

        # Check for context-specific commands
        if context.current_frame:
            # Look for context-aware commands
            context_commands = command_registry.get_commands_for_context(context.current_frame.type)
            for cmd_meta in context_commands:
                if cmd_meta.name == command_name or command_name in cmd_meta.aliases:
                    return self._execute_context_command(cmd_meta.name, parsed_cmd, context)

        # Check if we're in volttron context and handle special commands
        if (
            context.current_frame
            and context.current_frame.type == ContextType.VOLTTRON
            and command_name in ["deploy", "upload", "list", "status"]
        ):
            return self._execute_volttron_command(parsed_cmd, context)

        # Execute as CLI command
        return self._execute_cli_command(parsed_cmd, context)

    def _execute_repl_command(self, parsed_cmd: ParsedCommand, context: ReplContext) -> Any:
        """Execute REPL-specific commands."""
        command_name = parsed_cmd.command_path[0]
        args = parsed_cmd.arguments

        # Get the command metadata
        cmd_meta = command_registry.get_command(command_name)
        if not cmd_meta:
            # Check aliases
            for _cmd_name, meta in command_registry._commands.items():
                if command_name in meta.aliases:
                    cmd_meta = meta
                    break

        if not cmd_meta:
            raise click.ClickException(f"Unknown REPL command: {command_name}")

        # If it's a function-based REPL command
        if callable(cmd_meta.command_class) and not hasattr(cmd_meta.command_class, '__init__'):
            # It's a function, not a class
            return cmd_meta.command_class(args, context, self)

        # If it's a class-based command
        cmd_instance = command_registry.get_command_instance(cmd_meta.name, context)
        if cmd_instance:
            # Create a temporary click context for the command
            click_cmd = cmd_instance.get_click_command()

            # Build args for the command
            args_list = self._build_command_args(parsed_cmd, click_cmd)

            try:
                with click_cmd.make_context(
                    info_name=command_name,
                    args=args_list,
                    parent=self.click_ctx,
                ) as cmd_ctx:
                    cmd_ctx.obj = self.click_ctx.obj
                    return click_cmd.invoke(cmd_ctx)
            except click.ClickException:
                raise
            except Exception as e:
                raise click.ClickException(str(e)) from e

        # Fallback to simple execution for function-based commands
        # Look for the function in the repl module
        try:
            import aceiot_models_cli.commands.repl as repl_module
            func = getattr(repl_module, f"{command_name}_command", None)
            if func:
                return func(args, context, self)
        except (ImportError, AttributeError):
            pass

        raise click.ClickException(f"Cannot execute REPL command: {command_name}")

    def _execute_context_command(
        self, command_name: str, parsed_cmd: ParsedCommand, context: ReplContext
    ) -> Any:
        """Execute a context-aware command."""
        # Get command instance with context
        cmd_instance = command_registry.get_command_instance(command_name, context)
        if not cmd_instance:
            raise click.ClickException(f"Command not found: {command_name}")

        # Get the click command
        click_cmd = cmd_instance.get_click_command()

        # Inject context arguments
        if hasattr(cmd_instance, 'inject_context_args'):
            # Merge context args into parsed command
            context_args = cmd_instance.get_context_args()
            for key, value in context_args.items():
                if key not in parsed_cmd.options:
                    parsed_cmd.context_args[key] = value

        # Build command args
        args_list = self._build_command_args(parsed_cmd, click_cmd)

        # Execute the command
        try:
            with click_cmd.make_context(
                info_name=command_name,
                args=args_list,
                parent=self.click_ctx,
            ) as cmd_ctx:
                cmd_ctx.obj = self.click_ctx.obj
                return click_cmd.invoke(cmd_ctx)
        except click.ClickException:
            raise
        except Exception as e:
            raise click.ClickException(str(e)) from e

    def _execute_cli_command(self, parsed_cmd: ParsedCommand, context: ReplContext) -> Any:
        """Execute CLI commands with context injection."""
        # Resolve the command in the CLI group
        current_group: click.Command | click.Group = self.click_group
        for cmd_name in parsed_cmd.command_path:
            if isinstance(current_group, click.Group) and cmd_name in current_group.commands:
                current_group = current_group.commands[cmd_name]
            else:
                raise click.ClickException(
                    f"Command not found: {' '.join(parsed_cmd.command_path)}"
                )

        if not isinstance(current_group, click.Command):
            raise click.ClickException(f"Invalid command: {' '.join(parsed_cmd.command_path)}")

        # Apply context injection for specific commands
        self._apply_context_injection(parsed_cmd, context)

        # Build command line args list
        args = self._build_command_args(parsed_cmd, current_group)

        # Create a new context for command execution
        try:
            with current_group.make_context(
                info_name=" ".join(parsed_cmd.command_path),
                args=args,
                parent=self.click_ctx,
                allow_extra_args=True,
                allow_interspersed_args=False,
            ) as cmd_ctx:
                # Copy parent context object
                cmd_ctx.obj = self.click_ctx.obj
                # Invoke the command
                return current_group.invoke(cmd_ctx)
        except click.ClickException:
            raise
        except Exception as e:
            raise click.ClickException(f"Command execution failed: {e}") from e

    def _apply_context_injection(self, parsed_cmd: ParsedCommand, context: ReplContext) -> None:
        """Apply context-specific argument injection."""
        # This handles special cases for commands that need context injection
        # but aren't registered as context commands

        # Special handling for points list command in gateway context
        if (
            parsed_cmd.command_path == ["points", "list"]
            and context.current_gateway
            and "site" not in parsed_cmd.options
        ):
            # Get the gateway's site
            gateway_site = self._get_gateway_site(context.current_gateway)
            if gateway_site:
                parsed_cmd.context_args["site"] = gateway_site

        # Special handling for get commands in context
        if len(parsed_cmd.command_path) == 2 and parsed_cmd.command_path[1] == "get":
            entity_type = parsed_cmd.command_path[0]

            # If no argument provided, use current context
            if len(parsed_cmd.arguments) == 0:
                if entity_type == "clients" and context.current_client:
                    parsed_cmd.arguments = [context.current_client]
                elif entity_type == "sites" and context.current_site:
                    parsed_cmd.arguments = [context.current_site]
                elif entity_type == "gateways" and context.current_gateway:
                    parsed_cmd.arguments = [context.current_gateway]

    def _build_command_args(self, parsed_cmd: ParsedCommand, command: click.Command) -> list[str]:
        """Build command line arguments list with context injection."""
        args = []

        # Get parameter info
        param_map = {param.name: param for param in command.params}

        # Add context arguments as options if they match command parameters
        for key, value in parsed_cmd.context_args.items():
            if key in param_map:
                param = param_map[key]
                if isinstance(param, click.Option):
                    # Find the option flag to use
                    opt_flag = None
                    for opt in param.opts:
                        if opt.startswith("--"):
                            opt_flag = opt
                            break
                    if opt_flag:
                        args.extend([opt_flag, str(value)])

        # Add user-provided options (these override context)
        for key, value in parsed_cmd.options.items():
            # Add the option with proper formatting
            if len(key) == 1:
                args.append(f"-{key}")
            else:
                args.append(f"--{key}")
            if value is not True:  # Skip for boolean flags
                args.append(str(value))

        # Add positional arguments
        args.extend(parsed_cmd.arguments)

        return args

    def _get_api_client(self) -> APIClient | None:
        """Get API client from context."""
        return self.click_ctx.obj.get("client")

    def _get_gateway_site(self, gateway_name: str) -> str | None:
        """Get the site associated with a gateway."""
        api_client = self._get_api_client()
        if not api_client:
            return None

        try:
            if gateway_name is not None:
                gateway = api_client.get_gateway(gateway_name)
            else:
                return None
            return gateway.get("site") or gateway.get("site_name")
        except Exception:
            return None

    def _switch_to_context(self, context_type: ContextType, name: str, context: ReplContext) -> str:
        """Switch to a specific context after validation."""
        # Get API client
        api_client = self._get_api_client()
        if not api_client:
            return "Error: API client not configured. Please set ACEIOT_API_KEY."

        # Check for mutually exclusive contexts
        if context_type == ContextType.CLIENT and context.current_gateway:
            context.reset_context()
            return "Exited gateway context. " + self._switch_to_context(
                context_type, name, context
            )
        if context_type == ContextType.GATEWAY and context.current_client:
            context.reset_context()
            return "Exited client context. " + self._switch_to_context(
                context_type, name, context
            )

        # Validate resource exists
        try:
            if context_type == ContextType.CLIENT:
                if name is not None:
                    api_client.get_client(name)
                else:
                    return "Error: Client name cannot be None"
            elif context_type == ContextType.SITE:
                api_client.get_site(name)
            elif context_type == ContextType.GATEWAY:
                gateways = api_client.get_gateways()
                gateway_names = [g.get("name", "") for g in gateways.get("items", [])]
                if name not in gateway_names:
                    raise ValueError(f"Gateway '{name}' not found")
            elif context_type == ContextType.VOLTTRON:
                if name and name != "volttron":
                    context.enter_context(context_type, name, data={"package_id": name})
                    return f"Switched to volttron context with package: {name}"
                context.enter_context(context_type, "volttron")
                return "Switched to volttron deployment context"

            # If we get here, resource exists (except for volttron which is handled above)
            if context_type != ContextType.VOLTTRON:
                context.enter_context(context_type, name)
                return f"Switched to {context_type.value} context: {name}"

        except Exception as e:
            return f"Error: Could not switch to {context_type.value} '{name}': {e}"

    def _interactive_context_selection(
        self, context_type: ContextType, context: ReplContext, filter_text: str | None = None
    ) -> str:
        """List resources and allow interactive selection with fuzzy matching."""
        # Get API client
        api_client = self._get_api_client()
        if not api_client:
            return "Error: API client not configured. Please set ACEIOT_API_KEY."

        try:
            # Get list of resources based on type
            if context_type == ContextType.CLIENT:
                result = api_client.get_clients(per_page=100)
                items = result.get("items", [])
                choices = [
                    (item.get("name", ""), item.get("nice_name", item.get("name", "")))
                    for item in items
                ]

            elif context_type == ContextType.SITE:
                params: dict[str, Any] = {"per_page": 100}
                if context.current_frame and context.current_frame.type == ContextType.CLIENT:
                    params["client_name"] = context.current_frame.name

                result = api_client.get_sites(**params)
                items = result.get("items", [])
                choices = [
                    (
                        item.get("name", ""),
                        f"{item.get('name', '')} ({item.get('client_name', '')})",
                    )
                    for item in items
                ]

            elif context_type == ContextType.GATEWAY:
                result = api_client.get_gateways(per_page=100)
                items = result.get("items", [])
                choices = [
                    (item.get("name", ""), f"{item.get('name', '')} ({item.get('site_name', '')})")
                    for item in items
                ]

            elif context_type == ContextType.VOLTTRON:
                choices = [("volttron", "Volttron deployment context")]

            else:
                return f"Interactive selection not implemented for {context_type.value}"

            if not choices:
                return f"No {context_type.value}s found"

            # Apply fuzzy filter if provided
            if filter_text:
                filtered_choices = self._fuzzy_match(filter_text, choices)
                
                if not filtered_choices:
                    # No matches found - show suggestions
                    return f"No {context_type.value}s found matching '{filter_text}'. Use 'use {context_type.value}' without a filter to see all options."
                
                choices = filtered_choices
            
            # If only one choice after filtering, auto-select
            if len(choices) == 1:
                selected_name = choices[0][0]
                click.echo(
                    f"\nAuto-selecting the only {context_type.value} matching filter: {selected_name}"
                )
                return self._switch_to_context(context_type, selected_name, context)

            # Show table of options
            title = f"Available {context_type.value}s"
            if filter_text:
                title += f" (filtered by '{filter_text}')"
            table = Table(title=title)
            table.add_column("#", style="cyan", width=4)
            table.add_column("Name", style="green")
            table.add_column("Description", style="yellow")

            for i, (name, desc) in enumerate(choices, 1):
                table.add_row(str(i), name, desc)

            self.console.print(table)

            # If only one choice, auto-select
            if len(choices) == 1:
                selected_name = choices[0][0]
                click.echo(
                    f"\nAuto-selecting the only available {context_type.value}: {selected_name}"
                )
            else:
                # Ask for selection by number
                click.echo(
                    f"\nEnter number (1-{len(choices)}) or press Ctrl+C to cancel: ", nl=False
                )
                try:
                    selection = click.prompt("", type=int, default=0, show_default=False)
                    if 1 <= selection <= len(choices):
                        selected_name = choices[selection - 1][0]
                    else:
                        return f"Invalid selection. Please enter a number between 1 and {len(choices)}"
                except (click.Abort, KeyboardInterrupt):
                    return "\nSelection cancelled"

            # Switch to selected context
            return self._switch_to_context(context_type, selected_name, context)

        except Exception as e:
            return f"Error listing {context_type.value}s: {e}"

    def _show_general_help(self, context: ReplContext) -> str:
        """Show general REPL help."""
        help_text = """
ACE IoT Models CLI - Interactive Mode

REPL Commands:
  help [command]         Show help for command or general help
  use <type> [<name>]    Switch to context (client, site, gateway)
                         Without name: list and select interactively
                         With name: fuzzy match and filter results
                         Auto-selects if only one match found
  get [options]          Get current context entity as JSON (default) or table
                         Options: -o/--output <json|table>, -f/--file <filename>
  back                   Exit current context
  context                Show current context
  clear                  Clear screen
  exit, quit             Exit REPL

Context Types:
  client [<name>]        Set client context (exclusive with gateway)
  site [<name>]          Set site context
  gateway [<name>]       Set gateway context (exclusive with client)
  volttron               Enter Volttron deployment context

Examples:
  use site               # List sites and select interactively
  use site demo-site     # Enter site context directly
  use site demo          # Fuzzy match sites containing "demo"
  use gateway west       # Filter gateways with "west" in name
  points list            # List points for current site
  back                   # Exit site context

All regular CLI commands work in REPL mode with automatic context injection.
"""

        # Add context-specific help
        if context.current_frame:
            if context.current_frame.type == ContextType.GATEWAY:
                # Special handling for gateway context to show BACnet commands
                help_text += """\n\nGateway Context Commands:
  get                  Get current gateway details
  trigger-scan         Trigger BACnet scan on current gateway
  deploy-points        Deploy point config to current gateway
  enable-bacnet        Enable BACnet on current gateway
  disable-bacnet       Disable BACnet on current gateway
  bacnet-status        Show BACnet configuration status

BACnet Examples:
  trigger-scan --scan-address 192.168.1.0/24
  bacnet-status
  enable-bacnet

Note: You can also use the full 'gateways <command>' form if needed."""
            elif context.current_frame.type == ContextType.SITE:
                help_text += """\n\nSite Context Commands:
  sites get            Get current site details
  points list          List points for current site
  gateways list        List gateways for current site
  timeseries           Export all timeseries data for current site"""
            elif context.current_frame.type == ContextType.CLIENT:
                help_text += """\n\nClient Context Commands:
  clients get          Get current client details
  sites list           List sites for current client"""

        return help_text.strip()

    def _execute_volttron_command(self, parsed_cmd: ParsedCommand, context: ReplContext) -> Any:
        """Execute volttron-specific commands in REPL."""
        command = parsed_cmd.command_path[0]
        args = parsed_cmd.arguments

        # Get or create volttron handler
        if not self.volttron_handler:
            api_client = self._get_api_client()
            if not api_client:
                return "Error: API client not configured"
            self.volttron_handler = VolttronReplHandler(api_client, self.console)

        if command == "deploy":
            if not args:
                return self.volttron_handler.handle_deploy_wizard(context)
            return self._execute_cli_command(parsed_cmd, context)

        if command == "upload":
            if not args:
                if context.current_gateway or context.current_client:
                    return "Usage: upload <path> (client/gateway will be auto-detected)"
                return "Usage: upload <path> <name> (client or gateway name)"
            if len(args) == 1:
                if context.current_gateway:
                    parsed_cmd.arguments.append(context.current_gateway)
                elif context.current_client:
                    parsed_cmd.arguments.append(context.current_client)
            parsed_cmd.command_path = ["volttron", "upload-agent"]
            return self._execute_cli_command(parsed_cmd, context)

        if command == "list":
            if args and args[0] == "packages":
                if len(args) < 2:
                    if context.current_client:
                        parsed_cmd.command_path = ["volttron", "list-packages"]
                        parsed_cmd.arguments = [context.current_client]
                        return self._execute_cli_command(parsed_cmd, context)
                    if context.current_gateway:
                        parsed_cmd.command_path = ["volttron", "list-packages"]
                        parsed_cmd.arguments = [context.current_gateway]
                        return self._execute_cli_command(parsed_cmd, context)
                    return "Usage: list packages <name> (client or gateway name, or use from context)"
                parsed_cmd.command_path = ["volttron", "list-packages"]
                parsed_cmd.arguments = args[1:]
                return self._execute_cli_command(parsed_cmd, context)
            return "Usage: list packages"

        if command == "status":
            if args:
                parsed_cmd.command_path = ["volttron", "get-config-package"]
                return self._execute_cli_command(parsed_cmd, context)
            if context.current_gateway:
                parsed_cmd.arguments = [context.current_gateway]
                parsed_cmd.command_path = ["volttron", "get-config-package"]
                return self._execute_cli_command(parsed_cmd, context)
            return "Usage: status <gateway> (or use from gateway context)"

        return f"Unknown volttron command: {command}"

    def _execute_bacnet_in_context(self, parsed_cmd: ParsedCommand, context: ReplContext) -> Any:
        """Execute BACnet command in gateway context."""
        command_name = parsed_cmd.command_path[0]
        gateway_name = context.current_gateway

        # Map BACnet commands to their gateway command equivalents
        command_map = {
            "trigger-scan": "gateways trigger-scan",
            "deploy-points": "gateways deploy-points",
            "enable-bacnet": "gateways enable-bacnet",
            "disable-bacnet": "gateways disable-bacnet",
            "bacnet-status": "gateways bacnet-status"
        }

        if command_name not in command_map:
            return f"Unknown BACnet command: {command_name}"

        # Build the full command with gateway name
        cli_command = command_map[command_name]
        parsed_cmd.command_path = cli_command.split()

        # Insert gateway name as first argument
        args = [gateway_name] + parsed_cmd.arguments
        parsed_cmd.arguments = args

        # Execute as CLI command
        return self._execute_cli_command(parsed_cmd, context)

    def _fuzzy_match(self, text: str, candidates: list[tuple[str, str]]) -> list[tuple[str, str]]:
        """Perform fuzzy matching on candidates.
        
        Args:
            text: Search text
            candidates: List of (name, description) tuples
            
        Returns:
            Filtered and sorted list of candidates
        """
        if not text:
            return candidates
            
        text_lower = text.lower()
        scored_candidates = []
        
        for name, desc in candidates:
            name_lower = name.lower()
            desc_lower = desc.lower()
            
            # Calculate match score
            score = 0
            
            # Exact match gets highest score
            if text_lower == name_lower:
                score = 1000
            # Prefix match gets high score
            elif name_lower.startswith(text_lower):
                score = 800
            # Contains match
            elif text_lower in name_lower:
                score = 500
                # Bonus for word boundary match
                if f"-{text_lower}" in name_lower or f"_{text_lower}" in name_lower:
                    score += 100
            # Description contains match
            elif text_lower in desc_lower:
                score = 200
            # Partial token matching (e.g., "dem sit" matches "demo-site")
            else:
                tokens = text_lower.split()
                if all(any(token in part for part in name_lower.split("-")) for token in tokens):
                    score = 300
                elif all(token in name_lower for token in tokens):
                    score = 250
                    
            if score > 0:
                scored_candidates.append((score, name, desc))
        
        # Sort by score (descending) and then by name
        scored_candidates.sort(key=lambda x: (-x[0], x[1]))
        
        # Return candidates without scores
        return [(name, desc) for _, name, desc in scored_candidates]

    # Compatibility methods for tests that call old executor methods directly
    def _handle_use_command(self, args: list[str], context: ReplContext) -> str:
        """Legacy method for compatibility with tests."""
        from ..commands.repl import use_command
        return use_command(args, context, self)

    def _handle_back_command(self, context: ReplContext) -> str:
        """Legacy method for compatibility with tests."""
        from ..commands.repl import back_command
        return back_command([], context, self)

    def _handle_exit_command(self, context: ReplContext) -> str:
        """Legacy method for compatibility with tests."""
        from ..commands.repl import exit_command
        return exit_command([], context, self)

    def _handle_help_command(self, args: list[str], context: ReplContext) -> str:
        """Legacy method for compatibility with tests."""
        from ..commands.repl import help_command
        return help_command(args, context, self)

    def _handle_context_command(self, context: ReplContext) -> str:
        """Legacy method for compatibility with tests."""
        from ..commands.repl import context_command
        return context_command([], context, self)

    def _handle_clear_command(self) -> str:
        """Legacy method for compatibility with tests."""
        from ..commands.repl import clear_command
        return clear_command([], None, self)
