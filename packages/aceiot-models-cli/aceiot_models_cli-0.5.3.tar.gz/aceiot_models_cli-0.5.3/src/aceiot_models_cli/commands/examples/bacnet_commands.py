"""Example: BACnet commands using new architecture."""


import click

from ...repl.context import ContextType
from ..base import ContextAwareCommand
from ..decorators import context_command
from ..utils import ErrorHandlerMixin, OutputFormatterMixin


@context_command(
    name="trigger-scan",
    context_types=[ContextType.GATEWAY],
    description="Trigger BACnet scan on current gateway",
    auto_inject={"gateway_name": "gateway_name"}
)
class TriggerBacnetScanCommand(ContextAwareCommand, ErrorHandlerMixin):
    """Trigger a BACnet scan on the gateway."""

    def get_click_command(self) -> click.Command:
        @click.command("trigger-scan")
        @click.option(
            "--scan-address",
            help="BACnet scan address (e.g., 192.168.1.0/24)"
        )
        @click.pass_context
        def trigger_scan(ctx: click.Context, scan_address: str | None) -> None:
            """Trigger a BACnet scan on the gateway."""
            gateway_name = self.current_gateway
            if not gateway_name:
                from ...formatters import print_error
                print_error("No gateway context set. Use 'use gateway <name>' first.")
                ctx.exit(1)

            try:
                client = self.require_api_client(ctx)

                # Build updates
                updates = {"trigger_scan": True}
                if scan_address:
                    updates["bacnet_scan_address"] = scan_address

                # Update gateway deploy_config
                if gateway_name is not None:
                    gateway = client.get_gateway(gateway_name)
                else:
                    from ...formatters import print_error
                    print_error("Gateway name cannot be None")
                    ctx.exit(1)
                deploy_config = gateway.get("deploy_config", {})
                deploy_config.update(updates)

                result = client.patch_gateway(gateway_name, {"deploy_config": deploy_config})

                from ...formatters import print_success
                print_success(f"BACnet scan triggered on gateway '{gateway_name}'")

                if scan_address:
                    click.echo(f"Scan address updated to: {scan_address}")

                # Show current scan status
                deploy_config = result.get("deploy_config", {})
                click.echo(f"Last scan: {deploy_config.get('last_scan', 'Never')}")

            except Exception as e:
                self.handle_api_error(e, ctx)

        return trigger_scan


@context_command(
    name="bacnet-status",
    context_types=[ContextType.GATEWAY],
    description="Show BACnet configuration status",
    auto_inject={"gateway_name": "gateway_name"}
)
class BacnetStatusCommand(ContextAwareCommand, OutputFormatterMixin, ErrorHandlerMixin):
    """Show BACnet configuration status for current gateway."""

    def get_click_command(self) -> click.Command:
        @click.command("bacnet-status")
        @click.option("-o", "--output", type=click.Choice(["table", "json"]), default="table")
        @click.pass_context
        def bacnet_status(ctx: click.Context, output: str) -> None:
            """Show BACnet configuration status."""
            gateway_name = self.current_gateway
            if not gateway_name:
                from ...formatters import print_error
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
                    self.format_output(bacnet_info, ctx)
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
                    click.echo()

                    click.echo("History:")
                    click.echo(f"  Last Scan: {deploy_config.get('last_scan', 'Never')}")
                    click.echo(f"  Last Deploy: {deploy_config.get('last_deploy', 'Never')}")

            except Exception as e:
                self.handle_api_error(e, ctx)

        return bacnet_status


@context_command(
    name="deploy-points",
    context_types=[ContextType.GATEWAY],
    description="Deploy points to current gateway",
    auto_inject={"gateway_name": "gateway_name"}
)
class DeployPointsCommand(ContextAwareCommand, ErrorHandlerMixin):
    """Deploy points to the gateway."""

    def get_click_command(self) -> click.Command:
        @click.command("deploy-points")
        @click.pass_context
        def deploy_points(ctx: click.Context) -> None:
            """Deploy points to the gateway."""
            gateway_name = self.current_gateway
            if not gateway_name:
                from ...formatters import print_error
                print_error("No gateway context set. Use 'use gateway <name>' first.")
                ctx.exit(1)

            try:
                client = self.require_api_client(ctx)

                # Update gateway deploy_config
                if gateway_name is not None:
                    gateway = client.get_gateway(gateway_name)
                else:
                    from ...formatters import print_error
                    print_error("Gateway name cannot be None")
                    ctx.exit(1)
                deploy_config = gateway.get("deploy_config", {})
                deploy_config["trigger_deploy"] = True

                result = client.patch_gateway(gateway_name, {"deploy_config": deploy_config})

                from ...formatters import print_success
                print_success(f"Point deployment triggered on gateway '{gateway_name}'")

                # Show deployment status
                deploy_config = result.get("deploy_config", {})
                click.echo(f"Last deploy: {deploy_config.get('last_deploy', 'Never')}")

            except Exception as e:
                self.handle_api_error(e, ctx)

        return deploy_points
