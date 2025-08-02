"""Volttron commands using new architecture."""

import shutil
import time
from pathlib import Path

import click
from rich.console import Console
from rich.progress import BarColumn, DownloadColumn, Progress, SpinnerColumn, TextColumn

from ..formatters import format_json, print_error, print_success
from .base import BaseCommand
from .decorators import command
from .utils import ErrorHandlerMixin, OutputFormatterMixin, PaginationMixin


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


@command(
    name="volttron.upload-agent",
    description="Upload a Volttron agent package"
)
class UploadAgentCommand(BaseCommand, ErrorHandlerMixin):
    """Upload a Volttron agent package to a client."""

    def get_click_command(self) -> click.Command:
        @click.command("upload-agent")
        @click.argument("path", type=click.Path(exists=True))
        @click.argument("name")
        @click.option("--name", "-n", "package_name", help="Package name (required)")
        @click.option("--description", "-d", help="Package description")
        @click.option(
            "--keep-archive", is_flag=True, help="Keep temporary archive file for troubleshooting"
        )
        @click.pass_context
        def upload_agent(
            ctx: click.Context,
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
            client = self.require_api_client(ctx)
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
                        client_name = gateway_info.get("client") or gateway_info.get("client_name")
                    else:
                        print_error("Gateway name cannot be None")
                        if 'temp_archive' in locals() and temp_archive and Path(temp_archive).exists() and not keep_archive:
                            Path(temp_archive).unlink()
                        ctx.exit(1)
                    if not client_name:
                        print_error(f"Could not determine client for gateway '{name}'")
                        if temp_archive and Path(temp_archive).exists() and not keep_archive:
                            Path(temp_archive).unlink()
                        ctx.exit(1)
                    if output_format != "json":
                        console.print(f"Using client '{client_name}' from gateway '{name}'")
                except Exception as e:
                    # If 404, assume it's a client name
                    from aceiot_models.api import APIError
                    if isinstance(e, APIError) and e.status_code == 404:
                        # It's probably a client name, use it as-is
                        client_name = name
                    else:
                        raise
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
                        progress_callback=progress_callback,
                    )

                if output_format == "json":
                    click.echo(format_json(result))
                else:
                    print_success(f"✓ Package '{package_name}' uploaded successfully!")
                    console.print(f"Package ID: {result.get('id', 'N/A')}")

            except Exception as e:
                self.handle_api_error(e, ctx, "upload package")
            finally:
                # Clean up temporary archive if needed
                if temp_archive and Path(temp_archive).exists() and not keep_archive:
                    try:
                        Path(temp_archive).unlink()
                        if output_format != "json":
                            console.print("✓ Temporary archive cleaned up")
                    except Exception:
                        pass

        return upload_agent


@command(
    name="volttron.create-config",
    description="Create a Volttron agent configuration"
)
class CreateConfigCommand(BaseCommand, ErrorHandlerMixin):
    """Create a Volttron agent configuration."""

    def get_click_command(self) -> click.Command:
        @click.command("create-config")
        @click.argument("file", type=click.Path(exists=True))
        @click.argument("gateway")
        @click.option("--name", "-n", help="Configuration name (defaults to filename)")
        @click.pass_context
        def create_config(
            ctx: click.Context,
            file: str,
            gateway: str,
            name: str | None,
        ) -> None:
            """Create a Volttron agent configuration.

            Upload a configuration file to be used by Volttron agents.
            The config will be associated with a specific gateway.

            \b
            Arguments:
              FILE     Path to configuration file (JSON)
              GATEWAY  Gateway name to associate with config
            """
            client = self.require_api_client(ctx)
            output_format = ctx.obj["output"]
            console = Console()

            file_path = Path(file)

            # Default name to filename without extension
            if not name:
                name = file_path.stem
                if output_format != "json":
                    console.print(f"Using config name: {name}")

            # Read and validate JSON
            try:
                import json
                with open(file_path) as f:
                    config_data = json.load(f)
            except json.JSONDecodeError as e:
                print_error(f"Invalid JSON in config file: {e}")
                ctx.exit(1)
            except Exception as e:
                print_error(f"Failed to read config file: {e}")
                ctx.exit(1)

            # Create the config
            try:
                result = client.create_agent_config(
                    name=name,
                    gateway_name=gateway,
                    config=config_data,
                )

                if output_format == "json":
                    click.echo(format_json(result))
                else:
                    print_success(f"✓ Configuration '{name}' created successfully!")
                    console.print(f"Config ID: {result.get('id', 'N/A')}")
                    console.print(f"Gateway: {gateway}")

            except Exception as e:
                self.handle_api_error(e, ctx, "create configuration")

        return create_config


@command(
    name="volttron.deploy",
    description="Deploy a Volttron agent to a gateway"
)
class DeployCommand(BaseCommand, ErrorHandlerMixin):
    """Deploy a Volttron agent to a gateway."""

    def get_click_command(self) -> click.Command:
        @click.command("deploy")
        @click.argument("gateway")
        @click.option("--volttron-agent", "-v", help="Volttron agent details (JSON)")
        @click.option("--agent-config", "-c", help="Agent config details (JSON)")
        @click.pass_context
        def deploy(
            ctx: click.Context,
            gateway: str,
            volttron_agent: str | None,
            agent_config: str | None,
        ) -> None:
            """Deploy a Volttron agent to a gateway.

            Deploy a previously uploaded agent package to a specific gateway.
            You must specify both the agent package and configuration.

            \b
            Arguments:
              GATEWAY  Gateway name to deploy to

            \b
            Options:
              --volttron-agent  JSON with package_id and identity
              --agent-config    JSON with config_id
            """
            client = self.require_api_client(ctx)
            output_format = ctx.obj["output"]
            console = Console()

            if not volttron_agent or not agent_config:
                print_error("Both --volttron-agent and --agent-config are required")
                console.print("\nExample:")
                console.print('  --volttron-agent \'{"package_id": 123, "identity": "my-agent"}\'')
                console.print('  --agent-config \'{"config_id": 456}\'')
                ctx.exit(1)

            # Parse JSON arguments
            try:
                import json
                volttron_data = json.loads(volttron_agent)
                config_data = json.loads(agent_config)
            except json.JSONDecodeError as e:
                print_error(f"Invalid JSON: {e}")
                ctx.exit(1)

            # Validate required fields
            if "package_id" not in volttron_data or "identity" not in volttron_data:
                print_error("volttron-agent must include 'package_id' and 'identity'")
                ctx.exit(1)
            if "config_id" not in config_data:
                print_error("agent-config must include 'config_id'")
                ctx.exit(1)

            # Get gateway info first
            try:
                if gateway is not None:
                    gateway_info = client.get_gateway(gateway)
                else:
                    print_error("Gateway name cannot be None")
                    ctx.exit(1)
                deploy_config = gateway_info.get("deploy_config", {})

                # Update deploy_config
                deploy_config["volttron_agent"] = volttron_data
                deploy_config["agent_config"] = config_data
                deploy_config["trigger_deploy"] = True

                # Update the gateway
                result = client.patch_gateway(gateway, {"deploy_config": deploy_config})

                if output_format == "json":
                    click.echo(format_json(result))
                else:
                    print_success(f"✓ Deployment triggered for gateway '{gateway}'")
                    console.print(f"Agent Identity: {volttron_data['identity']}")
                    console.print(f"Package ID: {volttron_data['package_id']}")
                    console.print(f"Config ID: {config_data['config_id']}")

            except Exception as e:
                self.handle_api_error(e, ctx, "deploy agent")

        return deploy


@command(
    name="volttron.quick-deploy",
    description="Quick deploy agent with upload and config"
)
class QuickDeployCommand(BaseCommand, ErrorHandlerMixin):
    """Quick deploy with automatic upload and config creation."""

    def get_click_command(self) -> click.Command:
        @click.command("quick-deploy")
        @click.argument("path", type=click.Path(exists=True))
        @click.argument("config", type=click.Path(exists=True))
        @click.argument("gateway")
        @click.option("--identity", "-i", help="Agent identity (defaults to package name)")
        @click.option("--description", "-d", help="Package description")
        @click.pass_context
        def quick_deploy(
            ctx: click.Context,
            path: str,
            config: str,
            gateway: str,
            identity: str | None,
            description: str | None,
        ) -> None:
            """Quick deploy an agent with automatic upload and config creation.

            This command combines upload-agent, create-config, and deploy into one step.

            \b
            Arguments:
              PATH     Path to agent directory or archive
              CONFIG   Path to configuration file (JSON)
              GATEWAY  Gateway name to deploy to
            """
            client = self.require_api_client(ctx)
            output_format = ctx.obj["output"]
            console = Console()

            # Step 1: Detect agent info
            path_obj = Path(path)
            package_name = None
            if path_obj.is_dir():
                detected_name, _ = detect_agent_info(path_obj)
                if detected_name:
                    package_name = detected_name
                    console.print(f"✓ Detected package name: {package_name}")

            if not package_name:
                print_error("Could not detect package name from directory")
                ctx.exit(1)

            # Use package name as identity if not specified
            if not identity:
                identity = package_name

            # Get gateway info to find client
            try:
                if gateway is not None:
                    gateway_info = client.get_gateway(gateway)
                else:
                    print_error("Gateway name cannot be None")
                    ctx.exit(1)
                client_name = gateway_info.get("client") or gateway_info.get("client_name")
                if not client_name:
                    print_error(f"Could not determine client for gateway '{gateway}'")
                    ctx.exit(1)
            except Exception as e:
                self.handle_api_error(e, ctx, "get gateway info")
                return

            console.print(f"\n📦 Quick Deploy: {package_name}")
            console.print(f"   Gateway: {gateway}")
            console.print(f"   Client: {client_name}")
            console.print(f"   Identity: {identity}\n")

            # Step 2: Upload agent
            console.print("Step 1/3: Uploading agent package...")
            temp_archive = None
            try:
                # Similar upload logic as upload-agent command
                # (simplified here for brevity)
                upload_path = str(path_obj)
                if path_obj.is_dir():
                    # Create archive
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    archive_name = f"{path_obj.name}-{timestamp}.tar.gz"
                    temp_archive = str(Path.cwd() / archive_name)
                    base_name = temp_archive.replace(".tar.gz", "")
                    shutil.make_archive(base_name, "gztar", path_obj)
                    upload_path = temp_archive

                # Upload
                package_result = client.upload_client_volttron_agent_package(
                    client_name,
                    upload_path,
                    package_name=package_name,
                    description=description,
                )
                package_id = package_result["id"]
                console.print(f"✓ Package uploaded (ID: {package_id})")

            except Exception as e:
                if temp_archive and Path(temp_archive).exists():
                    Path(temp_archive).unlink()
                self.handle_api_error(e, ctx, "upload package")
                return
            finally:
                if temp_archive and Path(temp_archive).exists():
                    Path(temp_archive).unlink()

            # Step 3: Create config
            console.print("\nStep 2/3: Creating configuration...")
            try:
                import json
                config_path = Path(config)
                with open(config_path) as f:
                    config_data = json.load(f)

                config_name = f"{package_name}-config"
                config_result = client.create_agent_config(
                    name=config_name,
                    gateway_name=gateway,
                    config=config_data,
                )
                config_id = config_result["id"]
                console.print(f"✓ Configuration created (ID: {config_id})")

            except Exception as e:
                self.handle_api_error(e, ctx, "create configuration")
                return

            # Step 4: Deploy
            console.print("\nStep 3/3: Deploying to gateway...")
            try:
                if gateway is not None:
                    gateway_info = client.get_gateway(gateway)
                else:
                    print_error("Gateway name cannot be None")
                    ctx.exit(1)
                deploy_config = gateway_info.get("deploy_config", {})

                deploy_config["volttron_agent"] = {
                    "package_id": package_id,
                    "identity": identity
                }
                deploy_config["agent_config"] = {
                    "config_id": config_id
                }
                deploy_config["trigger_deploy"] = True

                result = client.patch_gateway(gateway, {"deploy_config": deploy_config})

                if output_format == "json":
                    click.echo(format_json({
                        "package_id": package_id,
                        "config_id": config_id,
                        "gateway": gateway,
                        "identity": identity,
                    }))
                else:
                    print_success("\n✓ Quick deploy completed successfully!")
                    console.print(f"   Package: {package_name} (ID: {package_id})")
                    console.print(f"   Config: {config_name} (ID: {config_id})")
                    console.print(f"   Gateway: {gateway}")
                    console.print(f"   Identity: {identity}")

            except Exception as e:
                self.handle_api_error(e, ctx, "deploy agent")

        return quick_deploy


@command(
    name="volttron.list-packages",
    description="List Volttron packages for a client",
    aliases=["ls-packages"]
)
class ListPackagesCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin, PaginationMixin):
    """List Volttron packages for a client."""

    def get_click_command(self) -> click.Command:
        @click.command("list-packages")
        @click.argument("name")
        @click.option("--page", default=1, help="Page number")
        @click.option("--per-page", default=10, help="Results per page")
        @click.pass_context
        def list_packages(
            ctx: click.Context,
            name: str,
            page: int,
            per_page: int,
        ) -> None:
            """List Volttron packages for a client.

            Shows all agent packages available for deployment to gateways
            belonging to the specified client.

            \b
            Arguments:
              NAME  Client name or gateway name (gateway's client will be used)
            """
            client = self.require_api_client(ctx)

            # Determine if name is a client or gateway
            client_name = name
            try:
                # Try to get it as a gateway first
                try:
                    if name is not None:
                        gateway_info = client.get_gateway(name)
                        client_name = gateway_info.get("client") or gateway_info.get("client_name")
                    else:
                        print_error("Gateway name cannot be None")
                        if 'temp_archive' in locals() and temp_archive and Path(temp_archive).exists() and not keep_archive:
                            Path(temp_archive).unlink()
                        ctx.exit(1)
                    if not client_name:
                        print_error(f"Could not determine client for gateway '{name}'")
                        ctx.exit(1)
                except Exception as e:
                    from aceiot_models.api import APIError
                    if isinstance(e, APIError) and e.status_code == 404:
                        # It's probably a client name, use it as-is
                        client_name = name
                    else:
                        raise
            except Exception as e:
                self.handle_api_error(e, ctx, "determine client")
                return

            try:
                result = client.get_client_volttron_agent_packages(
                    client_name,
                    page=page,
                    per_page=per_page
                )
                self.format_output(result, ctx, title=f"Volttron Packages for {client_name}")
            except Exception as e:
                self.handle_api_error(e, ctx, "list packages")

        return list_packages


@command(
    name="volttron.get-config-package",
    description="Get deployed configuration for an agent"
)
class GetConfigPackageCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Get deployed configuration for a Volttron agent."""

    def get_click_command(self) -> click.Command:
        @click.command("get-config-package")
        @click.argument("gateway")
        @click.option("--agent-identity", "-a", required=True, help="Agent identity")
        @click.pass_context
        def get_config_package(
            ctx: click.Context,
            gateway: str,
            agent_identity: str,
        ) -> None:
            """Get the deployed configuration for a Volttron agent.

            Retrieves the current configuration deployed to a specific agent
            identity on a gateway.

            \b
            Arguments:
              GATEWAY  Gateway name
            """
            client = self.require_api_client(ctx)

            try:
                # Get gateway info
                if gateway is not None:
                    gateway_info = client.get_gateway(gateway)
                else:
                    print_error("Gateway name cannot be None")
                    ctx.exit(1)
                deploy_config = gateway_info.get("deploy_config", {})

                # Check if agent is deployed
                volttron_agent = deploy_config.get("volttron_agent", {})
                agent_config = deploy_config.get("agent_config", {})

                if volttron_agent.get("identity") != agent_identity:
                    print_error(f"Agent '{agent_identity}' is not deployed on gateway '{gateway}'")
                    ctx.exit(1)

                # Get the config details
                config_id = agent_config.get("config_id")
                if not config_id:
                    print_error("No configuration found for agent")
                    ctx.exit(1)

                # Fetch the actual config
                try:
                    config_data = client.get_agent_config(config_id)
                    self.format_output(config_data, ctx,
                        title=f"Configuration for {agent_identity} on {gateway}")
                except Exception:
                    # If we can't fetch the config, show what we have
                    result = {
                        "gateway": gateway,
                        "agent_identity": agent_identity,
                        "volttron_agent": volttron_agent,
                        "agent_config": agent_config,
                        "last_deploy": deploy_config.get("last_deploy", "Never"),
                    }
                    self.format_output(result, ctx,
                        title=f"Deployment Info for {agent_identity} on {gateway}")

            except Exception as e:
                self.handle_api_error(e, ctx, "get configuration")

        return get_config_package
