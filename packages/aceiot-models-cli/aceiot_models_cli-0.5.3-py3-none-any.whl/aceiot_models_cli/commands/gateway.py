"""Gateway and BACnet commands using new architecture."""


import click

from ..formatters import format_json, print_error, print_success
from ..repl.context import ContextType
from .base import BaseCommand, ContextAwareCommand
from .decorators import command, context_command
from .utils import ErrorHandlerMixin, OutputFormatterMixin, PaginationMixin


@command(
    name="gateways.list",
    description="List all gateways",
    aliases=["ls-gateways"]
)
class ListGatewaysCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin, PaginationMixin):
    """List all gateways with optional filtering."""

    def get_click_command(self) -> click.Command:
        @click.command("list")
        @click.option("--page", default=1, help="Page number")
        @click.option("--per-page", default=10, help="Results per page")
        @click.option("--show-archived", is_flag=True, help="Include archived gateways")
        @click.pass_context
        def list_gateways(
            ctx: click.Context,
            page: int,
            per_page: int,
            show_archived: bool,
        ) -> None:
            """List all gateways."""
            try:
                client = self.require_api_client(ctx)

                # Build parameters
                params = {
                    "page": page,
                    "per_page": per_page,
                }
                if show_archived:
                    params["show_archived"] = show_archived

                result = client.get_gateways(**params)
                self.format_output(result, ctx, title="Gateways")
            except Exception as e:
                self.handle_api_error(e, ctx, "list gateways")

        return list_gateways


@command(
    name="gateways.get",
    description="Get gateway details"
)
class GetGatewayCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Get details for a specific gateway."""

    def get_click_command(self) -> click.Command:
        @click.command("get")
        @click.argument("gateway_name")
        @click.pass_context
        def get_gateway(ctx: click.Context, gateway_name: str) -> None:
            """Get a specific gateway by name."""
            try:
                client = self.require_api_client(ctx)
                result = client.get_gateway(gateway_name)
                self.format_output(result, ctx, title=f"Gateway: {gateway_name}")
            except Exception as e:
                self.handle_api_error(e, ctx, "get gateway")

        return get_gateway


@context_command(
    name="get",
    context_types=[ContextType.GATEWAY],
    description="Get current gateway details",
    auto_inject={"gateway_name": "gateway_name"}
)
class GetCurrentGatewayCommand(ContextAwareCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Get details for the current gateway in context."""

    def get_click_command(self) -> click.Command:
        @click.command("get")
        @click.pass_context
        def get_current_gateway(ctx: click.Context) -> None:
            """Get current gateway details."""
            # Name will be auto-injected from context
            name = self.current_gateway
            if not name:
                print_error("No gateway context set. Use 'use gateway <name>' first.")
                ctx.exit(1)

            try:
                client = self.require_api_client(ctx)
                if name is not None:
                    result = client.get_gateway(name)
                else:
                    print_error("Gateway name cannot be None")
                    ctx.exit(1)
                self.format_output(result, ctx, title=f"Gateway: {name}")
            except Exception as e:
                self.handle_api_error(e, ctx, "get gateway")

        return get_current_gateway


# BACnet Commands

@command(
    name="gateways.trigger-scan",
    description="Trigger BACnet scan on gateway"
)
class TriggerBacnetScanCommand(BaseCommand, ErrorHandlerMixin):
    """Trigger a BACnet scan on the gateway."""

    def get_click_command(self) -> click.Command:
        @click.command("trigger-scan")
        @click.argument("gateway_name")
        @click.option(
            "--scan-address",
            help="BACnet scan address (e.g., 192.168.1.0/24)"
        )
        @click.pass_context
        def trigger_scan(ctx: click.Context, gateway_name: str, scan_address: str | None) -> None:
            """Trigger a BACnet scan on the gateway."""
            try:
                client = self.require_api_client(ctx)

                # Get current gateway
                if gateway_name is not None:
                    gateway = client.get_gateway(gateway_name)
                else:
                    print_error("Gateway name cannot be None")
                    ctx.exit(1)

                # Update deploy_config
                deploy_config = gateway.get("deploy_config", {})
                deploy_config["trigger_scan"] = True
                if scan_address:
                    deploy_config["bacnet_scan_address"] = scan_address

                # Update gateway with new deploy_config
                update_data = {"deploy_config": deploy_config}
                result = client.patch_gateway(gateway_name, update_data)

                print_success(f"BACnet scan triggered on gateway '{gateway_name}'")

                if scan_address:
                    click.echo(f"Scan address updated to: {scan_address}")

                # Show current scan status
                deploy_config = result.get("deploy_config", {})
                click.echo(f"Last scan: {deploy_config.get('last_scan', 'Never')}")

            except Exception as e:
                self.handle_api_error(e, ctx, "update gateway")

        return trigger_scan


@context_command(
    name="trigger-scan",
    context_types=[ContextType.GATEWAY],
    description="Trigger BACnet scan on current gateway",
    auto_inject={"gateway_name": "gateway_name"}
)
class TriggerBacnetScanContextCommand(ContextAwareCommand, ErrorHandlerMixin):
    """Trigger a BACnet scan on the current gateway in context."""

    def get_click_command(self) -> click.Command:
        @click.command("trigger-scan")
        @click.option(
            "--scan-address",
            help="BACnet scan address (e.g., 192.168.1.0/24)"
        )
        @click.pass_context
        def trigger_scan_context(ctx: click.Context, scan_address: str | None) -> None:
            """Trigger a BACnet scan on the current gateway."""
            gateway_name = self.current_gateway
            if not gateway_name:
                print_error("No gateway context set. Use 'use gateway <name>' first.")
                ctx.exit(1)

            try:
                client = self.require_api_client(ctx)

                # Get current gateway
                if gateway_name is not None:
                    gateway = client.get_gateway(gateway_name)
                else:
                    print_error("Gateway name cannot be None")
                    ctx.exit(1)

                # Update deploy_config
                deploy_config = gateway.get("deploy_config", {})
                deploy_config["trigger_scan"] = True
                if scan_address:
                    deploy_config["bacnet_scan_address"] = scan_address

                # Update gateway with new deploy_config
                update_data = {"deploy_config": deploy_config}
                result = client.patch_gateway(gateway_name, update_data)

                print_success(f"BACnet scan triggered on gateway '{gateway_name}'")

                if scan_address:
                    click.echo(f"Scan address updated to: {scan_address}")

                # Show current scan status
                deploy_config = result.get("deploy_config", {})
                click.echo(f"Last scan: {deploy_config.get('last_scan', 'Never')}")

            except Exception as e:
                self.handle_api_error(e, ctx, "update gateway")

        return trigger_scan_context


@command(
    name="gateways.bacnet-status",
    description="Show BACnet configuration status"
)
class BacnetStatusCommand(BaseCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Show BACnet configuration status for a gateway."""

    def get_click_command(self) -> click.Command:
        @click.command("bacnet-status")
        @click.argument("gateway_name")
        @click.option("-o", "--output", type=click.Choice(["table", "json"]), default="table")
        @click.pass_context
        def bacnet_status(ctx: click.Context, gateway_name: str, output: str) -> None:
            """Show BACnet configuration status."""
            try:
                client = self.require_api_client(ctx)
                if gateway_name is not None:
                    gateway = client.get_gateway(gateway_name)
                else:
                    print_error("Gateway name cannot be None")
                    ctx.exit(1)
                deploy_config = gateway.get("deploy_config", {})

                if output == "json":
                    # Extract BACnet-related fields
                    bacnet_info = {
                        "gateway": gateway_name,
                        "bacnet_enabled": deploy_config.get("deploy_bacnet", False),
                        "trigger_scan": deploy_config.get("trigger_scan", False),
                        "trigger_deploy": deploy_config.get("trigger_deploy", False),
                        "last_scan": deploy_config.get("last_scan"),
                        "last_deploy": deploy_config.get("last_deploy"),
                        "bacnet_scan_address": deploy_config.get("bacnet_scan_address"),
                        "bacnet_proxy_address": deploy_config.get("bacnet_proxy_address"),
                    }
                    click.echo(format_json(bacnet_info))
                else:
                    # Table format
                    click.echo(f"\nBACnet Status for Gateway: {gateway_name}")
                    click.echo("=" * 50)

                    click.echo(f"BACnet Enabled: {deploy_config.get('deploy_bacnet', False)}")
                    click.echo(f"Scan Pending: {deploy_config.get('trigger_scan', False)}")
                    click.echo(f"Deploy Pending: {deploy_config.get('trigger_deploy', False)}")
                    click.echo()

                    click.echo("Addresses:")
                    click.echo(f"  Scan Address: {deploy_config.get('bacnet_scan_address', 'Not configured')}")
                    click.echo(f"  Proxy Address: {deploy_config.get('bacnet_proxy_address', 'Not configured')}")

                    # Add Object IDs if available
                    scan_object_id = deploy_config.get('bacnet_scan_object_id')
                    proxy_object_id = deploy_config.get('bacnet_proxy_object_id')
                    if scan_object_id or proxy_object_id:
                        click.echo("\nObject IDs:")
                        if scan_object_id:
                            click.echo(f"  Scan Object ID: {scan_object_id}")
                        if proxy_object_id:
                            click.echo(f"  Proxy Object ID: {proxy_object_id}")

                    click.echo()

                    click.echo("History:")
                    click.echo(f"  Last Scan: {deploy_config.get('last_scan', 'Never')}")
                    click.echo(f"  Last Deploy: {deploy_config.get('last_deploy', 'Never')}")

            except Exception as e:
                self.handle_api_error(e, ctx, "get gateway status")

        return bacnet_status


@context_command(
    name="bacnet-status",
    context_types=[ContextType.GATEWAY],
    description="Show BACnet status for current gateway",
    auto_inject={"gateway_name": "gateway_name"}
)
class BacnetStatusContextCommand(ContextAwareCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Show BACnet configuration status for current gateway."""

    def get_click_command(self) -> click.Command:
        @click.command("bacnet-status")
        @click.option("-o", "--output", type=click.Choice(["table", "json"]), default="table")
        @click.pass_context
        def bacnet_status_context(ctx: click.Context, output: str) -> None:
            """Show BACnet configuration status."""
            gateway_name = self.current_gateway
            if not gateway_name:
                print_error("No gateway context set. Use 'use gateway <name>' first.")
                ctx.exit(1)

            try:
                client = self.require_api_client(ctx)
                if gateway_name is not None:
                    gateway = client.get_gateway(gateway_name)
                else:
                    print_error("Gateway name cannot be None")
                    ctx.exit(1)
                deploy_config = gateway.get("deploy_config", {})

                if output == "json":
                    # Extract BACnet-related fields
                    bacnet_info = {
                        "gateway": gateway_name,
                        "bacnet_enabled": deploy_config.get("deploy_bacnet", False),
                        "trigger_scan": deploy_config.get("trigger_scan", False),
                        "trigger_deploy": deploy_config.get("trigger_deploy", False),
                        "last_scan": deploy_config.get("last_scan"),
                        "last_deploy": deploy_config.get("last_deploy"),
                        "bacnet_scan_address": deploy_config.get("bacnet_scan_address"),
                        "bacnet_proxy_address": deploy_config.get("bacnet_proxy_address"),
                    }
                    click.echo(format_json(bacnet_info))
                else:
                    # Table format
                    click.echo(f"\nBACnet Status for Gateway: {gateway_name}")
                    click.echo("=" * 50)

                    click.echo(f"BACnet Enabled: {deploy_config.get('deploy_bacnet', False)}")
                    click.echo(f"Scan Pending: {deploy_config.get('trigger_scan', False)}")
                    click.echo(f"Deploy Pending: {deploy_config.get('trigger_deploy', False)}")
                    click.echo()

                    click.echo("Addresses:")
                    click.echo(f"  Scan Address: {deploy_config.get('bacnet_scan_address', 'Not configured')}")
                    click.echo(f"  Proxy Address: {deploy_config.get('bacnet_proxy_address', 'Not configured')}")

                    # Add Object IDs if available
                    scan_object_id = deploy_config.get('bacnet_scan_object_id')
                    proxy_object_id = deploy_config.get('bacnet_proxy_object_id')
                    if scan_object_id or proxy_object_id:
                        click.echo("\nObject IDs:")
                        if scan_object_id:
                            click.echo(f"  Scan Object ID: {scan_object_id}")
                        if proxy_object_id:
                            click.echo(f"  Proxy Object ID: {proxy_object_id}")

                    click.echo()

                    click.echo("History:")
                    click.echo(f"  Last Scan: {deploy_config.get('last_scan', 'Never')}")
                    click.echo(f"  Last Deploy: {deploy_config.get('last_deploy', 'Never')}")

            except Exception as e:
                self.handle_api_error(e, ctx, "get gateway status")

        return bacnet_status_context


# Additional BACnet commands (deploy-points, enable-bacnet, disable-bacnet) follow similar pattern...
