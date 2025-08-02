"""Volttron-specific REPL commands and helpers."""

import json
from pathlib import Path

import click
from aceiot_models.api import APIClient, APIError
from rich.console import Console
from rich.table import Table

from ..volttron_commands import detect_agent_info, get_api_error_detail, validate_agent_directory
from .context import ReplContext


class VolttronReplHandler:
    """Handler for Volttron-specific REPL commands."""

    def __init__(self, api_client: APIClient, console: Console):
        self.api_client = api_client
        self.console = console

    def handle_deploy_wizard(self, context: ReplContext) -> str:
        """Interactive deployment wizard."""
        self.console.print("[bold]Welcome to Volttron Agent Deployment![/bold]\n")
        self.console.print("This wizard will guide you through deploying an agent to a gateway.\n")

        # Step 1: Select gateway first (required for all operations)
        self.console.print("[cyan]Step 1: Select target gateway[/cyan]")
        gateway = self._select_gateway()
        if not gateway:
            return "Deployment cancelled."

        # Step 2: Upload agent package to the gateway
        self.console.print("\n[cyan]Step 2: Upload agent package to gateway[/cyan]")
        package_name = self._upload_package_to_gateway(gateway)
        if not package_name:
            return "Deployment cancelled."

        # Step 3: Create agent configuration on the gateway
        self.console.print("\n[cyan]Step 3: Create agent configuration[/cyan]")
        agent_identity = click.prompt(
            "Agent identity", default=package_name.lower().replace(" ", ".")
        )
        config_name = click.prompt("Configuration name", default="default")

        config_created = self._create_config_on_gateway(gateway, agent_identity, config_name)
        if not config_created:
            return "Deployment cancelled."

        # Step 4: Create deployment package
        self.console.print("\n[cyan]Step 4: Creating deployment package[/cyan]")

        # Summary
        self.console.print("\n[bold]Ready to deploy:[/bold]")
        self.console.print(f"  Gateway: {gateway}")
        self.console.print(f"  Package: {package_name}")
        self.console.print(f"  Agent Identity: {agent_identity}")
        self.console.print(f"  Config: {config_name}")

        if not click.confirm("\nProceed with deployment?"):
            return "Deployment cancelled."

        # Create deployment
        try:
            # Build deployment data
            volttron_agent_data = {
                "package_name": package_name,
                "agent_identity": agent_identity,
            }

            agent_config_data = {
                "agent_identity": agent_identity,
                "config_name": config_name,
            }

            with self.console.status("Creating deployment package...", spinner="dots"):
                self.api_client.create_gateway_volttron_agent_config_package(
                    gateway,
                    volttron_agent=volttron_agent_data,
                    agent_config=agent_config_data,
                )

            self.console.print("\n[green]✓ Deployment package created successfully![/green]")
            return ""

        except APIError as e:
            return f"Deployment failed: {get_api_error_detail(e)}"

    def _upload_package_to_gateway(self, gateway: str) -> str | None:
        """Upload agent package to a specific gateway."""
        choices = [
            "Upload new agent package",
            "Select from existing packages",
            "Enter package name manually",
        ]

        for i, choice in enumerate(choices, 1):
            self.console.print(f"  {i}) {choice}")

        selection = click.prompt("\nChoice", type=click.IntRange(1, len(choices)))

        if selection == 1:
            # Upload new package
            path = click.prompt("Enter path to agent directory or zip file")
            try:
                path_obj = Path(path)

                # Get package name
                package_name = None
                if path_obj.is_dir():
                    # Validate and detect info
                    errors = validate_agent_directory(path_obj)
                    if errors:
                        self.console.print("[red]Invalid agent directory:[/red]")
                        for error in errors:
                            self.console.print(f"  - {error}")
                        return None

                    detected_name, _ = detect_agent_info(path_obj)
                    if detected_name:
                        package_name = detected_name
                        self.console.print(f"✓ Detected package name: {package_name}")

                if not package_name:
                    package_name = click.prompt("Package name")

                description = click.prompt("Description (optional)", default="")

                # Get client name from gateway
                if gateway is not None:
                    gateway_info = self.api_client.get_gateway(gateway)
                else:
                    self.console.print("[red]Gateway name cannot be None[/red]")
                    return None
                client_name = gateway_info.get("client") or gateway_info.get("client_name")
                if not client_name:
                    self.console.print(
                        f"[red]Could not determine client for gateway '{gateway}'[/red]"
                    )
                    return None

                # Upload
                self.console.print(f"\nUploading package to client '{client_name}'...")
                self.api_client.upload_client_volttron_agent_package(
                    client_name,
                    path,
                    package_name=package_name,
                    description=description if description else None,
                )

                self.console.print("[green]✓ Package uploaded successfully![/green]")
                return package_name

            except Exception as e:
                self.console.print(f"[red]Upload failed: {e}[/red]")
                return None

        elif selection == 2:
            # Select from existing packages
            return self._select_existing_package(gateway)
        else:
            # Enter package name manually
            package_name = click.prompt("Enter existing package name")
            return package_name

    def _create_config_on_gateway(
        self, gateway: str, agent_identity: str, config_name: str
    ) -> dict | None:
        """Create agent configuration on a gateway."""
        choices = [
            "Create new configuration",
            "Skip (use default configuration)",
        ]

        for i, choice in enumerate(choices, 1):
            self.console.print(f"  {i}) {choice}")

        selection = click.prompt("\nChoice", type=click.IntRange(1, len(choices)))

        if selection == 1:
            # Create new config
            config_type = click.prompt(
                "Configuration type", type=click.Choice(["file", "inline"]), default="file"
            )

            if config_type == "file":
                path = click.prompt(
                    "Enter path to configuration file (JSON or YAML)", type=click.Path(exists=True)
                )
                try:
                    config_path = Path(path)
                    config_data = config_path.read_text()

                    # Try to parse as JSON/YAML to validate
                    if config_path.suffix.lower() in [".yaml", ".yml"]:
                        import yaml

                        yaml.safe_load(config_data)  # Validate YAML
                        self.console.print("✓ YAML configuration validated")
                    else:
                        json.loads(config_data)  # Validate JSON
                        self.console.print("✓ JSON configuration validated")

                except Exception as e:
                    self.console.print(f"[red]Failed to read/parse config file: {e}[/red]")
                    return None
            else:
                self.console.print("Enter configuration (JSON format, Ctrl+D when done):")
                lines = []
                while True:
                    try:
                        line = input()
                        lines.append(line)
                    except EOFError:
                        break
                config_data = "\n".join(lines)

            try:
                self.console.print(f"\nCreating configuration on gateway '{gateway}'...")
                # Create agent config using the new API method
                import hashlib

                # Calculate hash
                config_hash = hashlib.sha256(config_data.encode()).hexdigest()

                agent_config_obj = {
                    "agent_identity": agent_identity,
                    "config_name": config_name,
                    "config_hash": config_hash,
                    "blob": config_data,
                    "active": True,
                }

                result = self.api_client.create_gateway_agent_configs(
                    gateway,
                    [agent_config_obj],  # API expects a list
                )

                self.console.print("[green]✓ Configuration created successfully![/green]")
                return result

            except Exception as e:
                self.console.print(f"[red]Failed to create config: {e}[/red]")
                return None

        else:
            # Use default config
            return {"config_name": "default"}

    def _select_gateway(self) -> str | None:
        """Select target gateway."""
        try:
            result = self.api_client.get_gateways(per_page=100)
            items = result.get("items", [])

            if not items:
                self.console.print("No gateways found.")
                return None

            # Separate online and offline gateways
            online_gateways = [g for g in items if g.get("status") == "online"]
            offline_gateways = [g for g in items if g.get("status") != "online"]

            table = Table(title="Available Gateways")
            table.add_column("#", style="cyan")
            table.add_column("Name")
            table.add_column("Status")
            table.add_column("Site")

            all_gateways = online_gateways + offline_gateways
            for i, gw in enumerate(all_gateways, 1):
                status = gw.get("status", "unknown")
                style = "green" if status == "online" else "red"
                table.add_row(
                    str(i),
                    gw.get("name", ""),
                    f"[{style}]{status}[/{style}]",
                    gw.get("site_name", ""),
                )

            self.console.print(table)

            selection = click.prompt(
                f"\nEnter number (1-{len(all_gateways)}) or gateway name", type=str
            )

            # Check if numeric selection
            try:
                idx = int(selection) - 1
                if 0 <= idx < len(all_gateways):
                    selected = all_gateways[idx]
                    if selected.get("status") != "online" and not click.confirm(
                        f"\nWarning: Gateway '{selected.get('name')}' is {selected.get('status')}. Continue anyway?"
                    ):
                        return None
                    return selected.get("name")
            except ValueError:
                # Not a number, treat as gateway name
                return selection

        except Exception as e:
            self.console.print(f"[red]Error listing gateways: {e}[/red]")
            return None

    def _select_existing_package(self, gateway: str) -> str | None:
        """Select from existing Volttron packages."""
        try:
            # Get the gateway's client
            if gateway is not None:
                gateway_data = self.api_client.get_gateway(gateway)
            else:
                self.console.print("[red]Gateway name cannot be None[/red]")
                return None
            client_name = gateway_data.get("client") or gateway_data.get("client_name")

            if not client_name:
                self.console.print("[red]Could not determine client for gateway[/red]")
                return None

            # Get packages for the client
            result = self.api_client.get_client_volttron_agent_package_list(
                client_name, per_page=100
            )
            items = result.get("items", [])

            if not items:
                self.console.print("[yellow]No packages found for this client[/yellow]")
                return None

            # Display packages table
            table = Table(title=f"Available Volttron Packages for {client_name}")
            table.add_column("#", style="cyan")
            table.add_column("Package Name")
            table.add_column("Description")
            table.add_column("Created")

            for i, pkg in enumerate(items, 1):
                table.add_row(
                    str(i),
                    pkg.get("package_name", ""),
                    pkg.get("description", ""),
                    pkg.get("created", "")[:10],  # Just date
                )

            self.console.print(table)

            selection = click.prompt(f"\nEnter number (1-{len(items)}) or package name", type=str)

            # Check if numeric selection
            try:
                idx = int(selection) - 1
                if 0 <= idx < len(items):
                    return items[idx].get("package_name")
            except ValueError:
                # Not a number, treat as package name
                return selection

        except Exception as e:
            self.console.print(f"[red]Failed to list packages: {e}[/red]")
            return None
