"""Volttron-related CLI commands."""

import shutil
import time
from pathlib import Path
from typing import Any

import click
from aceiot_models.api import APIClient, APIError
from click import Context
from rich.console import Console
from rich.progress import BarColumn, DownloadColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .formatters import format_json, print_error


def get_api_error_detail(error: APIError) -> str:
    """Extract detailed error message from APIError.

    Args:
        error: The APIError exception

    Returns:
        Detailed error message
    """
    if error.response_data and isinstance(error.response_data, dict):
        return error.response_data.get("detail", str(error))
    return str(error)


def require_api_client(ctx: Context) -> APIClient:
    """Ensure API client is available, exit if not."""
    if "client" not in ctx.obj:
        print_error("API key is required. Set ACEIOT_API_KEY or use --api-key")
        ctx.exit(1)
    return ctx.obj["client"]


def detect_agent_info(directory: Path) -> tuple[str | None, str | None]:
    """Detect agent name and version from setup.py file."""
    setup_py = directory / "setup.py"
    if not setup_py.exists():
        return None, None

    try:
        content = setup_py.read_text()
        name = None
        version = None

        # Simple parsing - look for name and version
        import re

        # Look for name in various formats
        name_patterns = [
            r'name\s*=\s*["\']([^"\']+)["\']',  # name = "package" or name = 'package'
            r"name\s*=\s*([^,\s]+)",  # name = package (without quotes)
        ]

        for pattern in name_patterns:
            match = re.search(pattern, content)
            if match:
                name = match.group(1).strip()
                # Clean up any trailing commas or parentheses
                name = name.rstrip(",)")
                break

        # Look for version in various formats
        version_patterns = [
            r'version\s*=\s*["\']([^"\']+)["\']',  # version = "1.0" or version = '1.0'
            r"version\s*=\s*([^,\s]+)",  # version = 1.0 (without quotes)
        ]

        for pattern in version_patterns:
            match = re.search(pattern, content)
            if match:
                version = match.group(1).strip()
                # Clean up any trailing commas or parentheses
                version = version.rstrip(",)")
                break

        return name, version
    except Exception:
        return None, None


def validate_agent_directory(directory: Path) -> list[str]:
    """Validate that directory contains required Volttron agent files."""
    errors = []

    # Check for required files
    required_files = ["setup.py"]
    for file in required_files:
        if not (directory / file).exists():
            errors.append(f"Missing required file: {file}")

    # Check for agent code (at least one .py file)
    py_files = list(directory.glob("**/*.py"))
    if len(py_files) == 0:
        errors.append("No Python files found in agent directory")

    return errors


# Volttron commands group
@click.group()
@click.pass_context
def volttron(ctx: Context) -> None:
    """Manage Volttron agent deployments."""


@volttron.command("upload-agent")
@click.argument("path", type=click.Path(exists=True))
@click.argument("name")
@click.option("--name", "-n", "package_name", help="Package name (required)")
@click.option("--description", "-d", help="Package description")
@click.option(
    "--keep-archive", is_flag=True, help="Keep temporary archive file for troubleshooting"
)
@click.pass_context
def upload_agent(
    ctx: Context,
    path: str,
    name: str,
    package_name: str | None,
    description: str | None,
    keep_archive: bool,
) -> None:
    """Upload a Volttron agent package to a client.

    The package is uploaded to the specified client. If a gateway name is provided,
    the client that owns that gateway will be used. Packages are shared across
    all gateways belonging to the same client.

    Directories are automatically compressed to tar.gz format before upload.
    Use --keep-archive to retain the temporary archive file for troubleshooting.

    \b
    Arguments:
      PATH  Path to agent directory or tar.gz/zip file
      NAME  Client name or gateway name (gateway's client will be used)
    """
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]
    console = Console()

    path_obj = Path(path)

    # Package name is required
    if not package_name:
        # Try to detect from directory
        if path_obj.is_dir():
            detected_name, detected_version = detect_agent_info(path_obj)
            if detected_name:
                package_name = detected_name
                console.print(f"✓ Detected package name: {package_name}")

        if not package_name:
            print_error("Package name is required. Use --name to specify.")
            ctx.exit(1)

    # Validate if directory
    temp_archive = None
    if path_obj.is_dir():
        console.print("Preparing agent package...")

        # Validate directory structure
        errors = validate_agent_directory(path_obj)
        if errors:
            print_error("Invalid agent directory structure:")
            for error in errors:
                console.print(f"  - {error}")
            ctx.exit(1)

        console.print("✓ Directory structure validated")
        console.print("✓ Creating tar.gz archive...")

        # Create temporary archive
        try:
            # Create a temporary file in the current working directory
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            archive_name = f"{path_obj.name}-{timestamp}.tar.gz"
            temp_archive = str(Path.cwd() / archive_name)

            # Create the archive
            base_name = temp_archive.replace(".tar.gz", "")
            shutil.make_archive(base_name, "gztar", path_obj)

            upload_path = temp_archive
            console.print(f"✓ Created temporary archive: {archive_name}")
            if keep_archive:
                console.print(f"ℹ️  Archive will be kept at: {temp_archive}")
        except Exception as e:
            if temp_archive and Path(temp_archive).exists() and not keep_archive:
                Path(temp_archive).unlink()
            print_error(f"Failed to create archive: {e}")
            ctx.exit(1)
    else:
        upload_path = str(path_obj)

    # Determine if name is a client or gateway
    client_name = name
    try:
        # Try to get it as a gateway first
        try:
            if name is not None:
                gateway_info = client.get_gateway(name)
            else:
                print_error("Gateway name cannot be None")
                if 'temp_archive' in locals() and temp_archive and Path(temp_archive).exists() and not keep_archive:
                    Path(temp_archive).unlink()
                ctx.exit(1)
            client_name = gateway_info.get("client") or gateway_info.get("client_name")
            if not client_name:
                print_error(f"Could not determine client for gateway '{name}'")
                if temp_archive and Path(temp_archive).exists() and not keep_archive:
                    Path(temp_archive).unlink()
                ctx.exit(1)
            if output_format != "json":
                console.print(f"Using client '{client_name}' from gateway '{name}'")
        except APIError as e:
            # If 404, assume it's a client name, otherwise re-raise
            if e.status_code != 404:
                print_error(f"Failed to get gateway info: {get_api_error_detail(e)}")
                if temp_archive and Path(temp_archive).exists() and not keep_archive:
                    Path(temp_archive).unlink()
                ctx.exit(1)
            # It's probably a client name, use it as-is
            client_name = name
    except Exception as e:
        print_error(f"Failed to determine client: {e}")
        if temp_archive and Path(temp_archive).exists() and not keep_archive:
            Path(temp_archive).unlink()
        ctx.exit(1)

    # Upload with progress
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            console=console,
        ) as progress:
            upload_task = progress.add_task("Uploading to Aerodrome Cloud...", total=None)

            def progress_callback(bytes_read: int, total_size: int):
                progress.update(upload_task, completed=bytes_read, total=total_size)

            result = client.upload_client_volttron_agent_package(
                client_name,
                upload_path,
                package_name=package_name,
                description=description,
            )

        if output_format == "json":
            click.echo(format_json(result))
        else:
            console.print("\n[green]Agent package uploaded successfully![/green]")
            console.print(f"Package ID: [bold]{result.get('id', 'N/A')}[/bold]")
            if result.get("name"):
                console.print(f"Name: {result['name']}")
            if result.get("version"):
                console.print(f"Version: {result['version']}")
            if result.get("size"):
                console.print(f"Size: {result['size']:,} bytes")
            if result.get("upload_time"):
                console.print(f"Upload time: {result['upload_time']}")

    except APIError as e:
        print_error(f"Upload failed: {get_api_error_detail(e)}")
        if temp_archive and Path(temp_archive).exists() and not keep_archive:
            Path(temp_archive).unlink()
        ctx.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if temp_archive and Path(temp_archive).exists() and not keep_archive:
            Path(temp_archive).unlink()
        ctx.exit(1)
    finally:
        # Clean up temporary archive
        if temp_archive and Path(temp_archive).exists():
            if keep_archive:
                console.print(f"\n[yellow]ℹ️  Temporary archive kept at: {temp_archive}[/yellow]")
            else:
                Path(temp_archive).unlink()
                console.print("✓ Cleaned up temporary archive")


@volttron.command("create-config")
@click.argument("file", type=click.Path(exists=True))
@click.argument("gateway")
@click.option("--name", "-n", help="Configuration name (defaults to filename)")
@click.option("--agent-identity", "-a", required=True, help="Agent identity (required)")
@click.option("--active/--no-active", default=True, help="Whether config is active")
@click.option("--validate/--no-validate", default=True, help="Validate configuration before upload")
@click.pass_context
def create_config(
    ctx: Context,
    file: str,
    gateway: str,
    name: str | None,
    agent_identity: str,
    active: bool,
    validate: bool,
) -> None:
    """Create an agent configuration on a gateway.

    \b
    Arguments:
      FILE     Configuration file (JSON or YAML)
      GATEWAY  Target gateway name
    """
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]
    console = Console()

    file_path = Path(file)

    # Default name to filename without extension
    if not name:
        name = file_path.stem

    # Read configuration file
    content = file_path.read_text()

    # Validate configuration if requested
    if validate:
        console.print("Validating configuration...")
        try:
            import json

            import yaml

            if file_path.suffix in [".yaml", ".yml"]:
                yaml.safe_load(content)
            else:
                json.loads(content)
            console.print("✓ Configuration valid")
        except Exception as e:
            print_error(f"Configuration validation failed: {e}")
            ctx.exit(1)

    # Create configuration
    try:
        console.print("\nCreating agent configuration...")

        # Create agent config using the new API method
        import hashlib
        import json as json_lib

        # Convert content to dict if it's a string
        config_blob = content if isinstance(content, str) else json_lib.dumps(content)

        # Calculate hash
        config_hash = hashlib.sha256(config_blob.encode()).hexdigest()

        agent_config = {
            "agent_identity": agent_identity,
            "config_name": name,
            "config_hash": config_hash,
            "blob": config_blob,
            "active": active,
        }

        result = client.create_gateway_agent_configs(
            gateway,
            [agent_config],  # API expects a list
        )

        if output_format == "json":
            click.echo(format_json(result))
        else:
            console.print("[green]✓ Configuration created successfully![/green]\n")
            console.print(f"Config Name: [bold]{result.get('config_name', name)}[/bold]")
            console.print(f"Agent Identity: {result.get('agent_identity', agent_identity)}")
            console.print(f"Config Hash: {result.get('config_hash', 'N/A')}")
            console.print(f"Active: {result.get('active', active)}")

    except APIError as e:
        print_error(f"Configuration creation failed: {get_api_error_detail(e)}")
        ctx.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        ctx.exit(1)


@volttron.command("deploy")
@click.argument("gateway")
@click.option("--volttron-agent", "-v", help="Volttron agent details (JSON)")
@click.option("--agent-config", "-c", help="Agent config details (JSON)")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode with package selection")
@click.pass_context
def deploy(
    ctx: Context,
    gateway: str,
    volttron_agent: str | None,
    agent_config: str | None,
    interactive: bool,
) -> None:
    """Create a Volttron agent config package (deployment) on a gateway.

    \b
    Arguments:
      GATEWAY  Target gateway name
    """
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]
    console = Console()

    # Parse JSON inputs
    import json

    volttron_agent_data: dict[str, Any] | None = None
    agent_config_data: dict[str, Any] | None = None

    # If no options provided, enable interactive mode
    if not volttron_agent and not agent_config:
        interactive = True

    if interactive:
        # Interactive mode - let user select from existing packages
        console.print("[bold]Interactive Volttron Deployment[/bold]\n")

        # Get gateway info to find client
        try:
            if gateway is not None:
                gateway_info = client.get_gateway(gateway)
            else:
                print_error("Gateway name cannot be None")
                ctx.exit(1)
            client_name = gateway_info.get("client") or gateway_info.get("client_name")

            if not client_name:
                print_error("Could not determine client for gateway")
                ctx.exit(1)

            # List available packages
            result = client.get_client_volttron_agent_package_list(client_name, per_page=100)
            items = result.get("items", [])

            if not items:
                console.print("[yellow]No packages found for this client[/yellow]")
                console.print("Please upload a package first using: volttron upload-agent")
                ctx.exit(1)

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
                    pkg.get("created", "")[:10],
                )

            console.print(table)

            # Get selection
            selection = click.prompt("\nEnter number to select package", type=int)
            if 1 <= selection <= len(items):
                selected_package = items[selection - 1].get("package_name")
            else:
                print_error("Invalid selection")
                ctx.exit(1)

            # Get agent identity
            agent_identity = click.prompt(
                "\nEnter agent identity", default=selected_package.lower().replace(" ", ".")
            )

            # Ask about configuration
            config_choice = click.prompt(
                "\nConfiguration", type=click.Choice(["default", "custom"]), default="default"
            )

            config_name = "default"
            config_data = ""  # Initialize as empty string

            if config_choice == "custom":
                config_name = click.prompt("Configuration name")

                # Ask for config file path
                config_file_path = click.prompt(
                    "Enter path to configuration file (JSON or YAML)", type=click.Path(exists=True)
                )

                # Read and validate config file
                try:
                    import json
                    from pathlib import Path

                    import yaml

                    config_path = Path(config_file_path)
                    content = config_path.read_text()

                    # Validate the configuration
                    if config_path.suffix.lower() in [".yaml", ".yml"]:
                        yaml.safe_load(content)  # Validate YAML
                    else:
                        json.loads(content)  # Validate JSON

                    config_data = content
                    console.print(f"✓ Configuration file loaded: {config_file_path}")

                except Exception as e:
                    print_error(f"Failed to read/validate config file: {e}")
                    ctx.exit(1)

                # Create the configuration on the gateway first
                try:
                    console.print(f"\nCreating configuration '{config_name}' on gateway...")
                    # Create agent config using the new API method
                    import hashlib

                    # Calculate hash
                    config_hash = hashlib.sha256(config_data.encode()).hexdigest()

                    agent_config_dict = {
                        "agent_identity": agent_identity,
                        "config_name": config_name,
                        "config_hash": config_hash,
                        "blob": config_data,
                        "active": True,
                    }

                    client.create_gateway_agent_configs(
                        gateway,
                        [agent_config_dict],  # API expects a list
                    )
                    console.print("[green]✓ Configuration created successfully[/green]")
                except Exception as e:
                    print_error(f"Failed to create configuration: {e}")
                    ctx.exit(1)

            # Build deployment data
            volttron_agent_data = {
                "package_name": selected_package,
                "agent_identity": agent_identity,
            }

            agent_config_data = {
                "agent_identity": agent_identity,
                "config_name": config_name,
            }

        except Exception as e:
            print_error(f"Interactive mode failed: {e}")
            ctx.exit(1)

    else:
        # Non-interactive mode - parse provided options
        if volttron_agent:
            try:
                volttron_agent_data = json.loads(volttron_agent)
            except json.JSONDecodeError as e:
                print_error(f"Invalid JSON for volttron-agent: {e}")
                ctx.exit(1)

        if agent_config:
            try:
                agent_config_data = json.loads(agent_config)
            except json.JSONDecodeError as e:
                print_error(f"Invalid JSON for agent-config: {e}")
                ctx.exit(1)

        if not volttron_agent_data and not agent_config_data:
            print_error("At least one of --volttron-agent or --agent-config must be provided")
            ctx.exit(1)

    # Show deployment summary
    console.print("Creating Volttron agent config package...")
    console.print(f"Gateway: [bold]{gateway}[/bold]")
    if volttron_agent_data:
        console.print(f"Volttron Agent: {json.dumps(volttron_agent_data)}")
    if agent_config_data:
        console.print(f"Agent Config: {json.dumps(agent_config_data)}")

    try:
        with console.status("Creating deployment...", spinner="dots"):
            # Ensure we have at least volttron_agent data
            if not volttron_agent_data:
                print_error("Volttron agent data is required")
                ctx.exit(1)

            result = client.create_gateway_volttron_agent_config_package(
                gateway,
                volttron_agent=volttron_agent_data,
                agent_config=agent_config_data,
            )

        if output_format == "json":
            click.echo(format_json(result))
        else:
            console.print("\n[green]Agent deployed successfully![/green]")
            console.print(f"Deployment ID: [bold]{result.get('id', 'N/A')}[/bold]")
            if result.get("agent_identity"):
                console.print(f"Agent Identity: {result['agent_identity']}")
            if result.get("status"):
                console.print(f"Status: {result['status']}")
            if result.get("started"):
                console.print(f"Started: {result['started']}")

    except APIError as e:
        print_error(f"Deployment failed: {get_api_error_detail(e)}")
        ctx.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        ctx.exit(1)


@volttron.command("quick-deploy")
@click.argument("path", type=click.Path(exists=True))
@click.argument("config", type=click.Path(exists=True))
@click.argument("gateway")
@click.option("--package-name", "-n", help="Agent package name")
@click.option("--description", "-d", help="Package description")
@click.option("--config-name", help="Configuration name")
@click.option("--agent-identity", "-a", required=True, help="Agent identity (required)")
@click.option("--active/--no-active", default=True, help="Whether config is active")
@click.option("--skip-validation", is_flag=True, help="Skip validation steps")
@click.pass_context
def quick_deploy(
    ctx: Context,
    path: str,
    config: str,
    gateway: str,
    package_name: str | None,
    description: str | None,
    config_name: str | None,
    agent_identity: str,
    active: bool,
    skip_validation: bool,
) -> None:
    """Deploy a Volttron agent in one command.

    This combines upload-agent, upload-config, and deploy into a single operation.

    \b
    Arguments:
      PATH     Path to agent directory or zip file
      CONFIG   Path to configuration file
      GATEWAY  Target gateway name
    """
    console = Console()
    console.print("[bold]Quick Deploy - Volttron Agent[/bold]\n")

    # Step 1: Upload agent package
    console.print("[cyan]Step 1/3: Uploading agent package[/cyan]")
    ctx.invoke(
        upload_agent,
        path=path,
        name=gateway,
        package_name=package_name,
        description=description,
        keep_archive=False,  # Don't keep archive in quick-deploy
    )

    # Step 2: Create configuration
    console.print("\n[cyan]Step 2/3: Creating agent configuration[/cyan]")
    ctx.invoke(
        create_config,
        file=config,
        gateway=gateway,
        name=config_name,
        agent_identity=agent_identity,
        active=active,
        validate=not skip_validation,
    )

    # Step 3: Deploy
    console.print("\n[cyan]Step 3/3: Creating deployment package[/cyan]")
    console.print("[yellow]Note: Full deployment integration pending API clarification[/yellow]")


@volttron.command("list-packages")
@click.argument("name")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=10, help="Results per page")
@click.pass_context
def list_packages(ctx: Context, name: str, page: int, per_page: int) -> None:
    """List Volttron agent packages for a client.

    \b
    Arguments:
      NAME  Client name or gateway name (gateway's client will be used)
    """
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    # Determine if name is a client or gateway
    client_name = name
    try:
        # Try to get it as a gateway first
        try:
            if name is not None:
                gateway_info = client.get_gateway(name)
            else:
                print_error("Gateway name cannot be None")
                if 'temp_archive' in locals() and temp_archive and Path(temp_archive).exists() and not keep_archive:
                    Path(temp_archive).unlink()
                ctx.exit(1)
            client_name = gateway_info.get("client") or gateway_info.get("client_name")
            if not client_name:
                print_error(f"Could not determine client for gateway '{name}'")
                ctx.exit(1)
            if output_format != "json":
                console = Console()
                console.print(f"Using client '{client_name}' from gateway '{name}'")
        except APIError as e:
            # If 404, assume it's a client name, otherwise re-raise
            if e.status_code != 404:
                raise
            # It's probably a client name, use it as-is
            client_name = name

        result = client.get_client_volttron_agent_package_list(
            client_name, page=page, per_page=per_page
        )

        if output_format == "json":
            click.echo(format_json(result))
        else:
            items = result.get("items", [])
            if not items:
                click.echo("No packages found.")
                return

            table = Table(title="Volttron Agent Packages")
            table.add_column("#", style="dim")
            table.add_column("Package ID")
            table.add_column("Name")
            table.add_column("Version")
            table.add_column("Size")
            table.add_column("Uploaded")

            for idx, pkg in enumerate(items, 1):
                table.add_row(
                    str(idx),
                    pkg.get("id", ""),
                    pkg.get("package_name", ""),
                    pkg.get("object_hash", ""),
                    f"{pkg.get('size', 0):,} bytes" if pkg.get("size") else "",
                    pkg.get("created", ""),
                )

            console = Console()
            console.print(table)

            # Show pagination info
            total = result.get("total", 0)
            if total > per_page:
                console.print(
                    f"\nPage {page} of {(total + per_page - 1) // per_page} (Total: {total})"
                )

    except APIError as e:
        print_error(f"Failed to list packages: {get_api_error_detail(e)}")
        ctx.exit(1)


@volttron.command("get-config-package")
@click.argument("gateway")
@click.option("--agent-identity", "-a", required=True, help="Agent identity")
@click.pass_context
def get_config_package(ctx: Context, gateway: str, agent_identity: str) -> None:
    """Get Volttron agent config package for a gateway.

    \b
    Arguments:
      GATEWAY  Gateway name
    """
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        result = client.get_gateway_volttron_agent_config_package(gateway, agent_identity)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            console = Console()
            console.print(f"[bold]Volttron Agent Config Package for {gateway}[/bold]")
            if result.get("volttron_agent"):
                console.print("\n[cyan]Volttron Agent:[/cyan]")
                for key, value in result["volttron_agent"].items():
                    console.print(f"  {key}: {value}")
            if result.get("agent_config"):
                console.print("\n[cyan]Agent Config:[/cyan]")
                for key, value in result["agent_config"].items():
                    console.print(f"  {key}: {value}")

    except APIError as e:
        print_error(f"Failed to get config package: {get_api_error_detail(e)}")
        ctx.exit(1)
