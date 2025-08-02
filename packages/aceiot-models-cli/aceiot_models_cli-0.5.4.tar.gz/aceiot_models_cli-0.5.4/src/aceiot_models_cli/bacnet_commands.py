"""BACnet management commands for gateways."""

from typing import Any

import click
from aceiot_models.api import APIClient, APIError

from .formatters import format_json, print_error, print_success


def update_gateway_deploy_config(
    client: APIClient, gateway_name: str, updates: dict[str, Any]
) -> dict[str, Any]:
    """Update gateway deploy_config with semaphore values.
    
    Args:
        client: API client
        gateway_name: Name of the gateway
        updates: Dictionary of deploy_config updates
        
    Returns:
        Updated gateway data
    """
    try:
        # Get current gateway
        if gateway_name is None:
            click.echo("Error: Gateway name cannot be None")
            return None
        gateway = client.get_gateway(gateway_name)

        # Update deploy_config
        deploy_config = gateway.get("deploy_config", {})
        deploy_config.update(updates)

        # Update gateway with new deploy_config
        update_data = {"deploy_config": deploy_config}
        return client.patch_gateway(gateway_name, update_data)

    except APIError as e:
        raise click.ClickException(f"Failed to update gateway: {e}")


def get_api_error_detail(error: APIError) -> str:
    """Extract detailed error message from API error."""
    if error.response_data and isinstance(error.response_data, dict):
        return error.response_data.get("detail", str(error))
    return str(error)


@click.command("trigger-scan")
@click.argument("gateway_name")
@click.option(
    "--scan-address",
    help="BACnet scan address (e.g., 192.168.1.0/24). If not provided, uses existing address."
)
@click.pass_context
def trigger_bacnet_scan(ctx: click.Context, gateway_name: str, scan_address: str | None) -> None:
    """Trigger a BACnet scan on the gateway.
    
    This sets the trigger_scan semaphore to true in the gateway's deploy_config.
    Optionally updates the bacnet_scan_address if provided.
    """
    client = ctx.obj["client"]

    updates = {"trigger_scan": True}
    if scan_address:
        updates["bacnet_scan_address"] = scan_address

    try:
        result = update_gateway_deploy_config(client, gateway_name, updates)
        print_success(f"BACnet scan triggered on gateway '{gateway_name}'")

        if scan_address:
            click.echo(f"Scan address updated to: {scan_address}")

        # Show current scan status
        deploy_config = result.get("deploy_config", {})
        click.echo(f"Last scan: {deploy_config.get('last_scan', 'Never')}")

    except click.ClickException:
        raise
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        ctx.exit(1)


@click.command("deploy-points")
@click.argument("gateway_name")
@click.pass_context
def deploy_points(ctx: click.Context, gateway_name: str) -> None:
    """Deploy points to the gateway.
    
    This sets the trigger_deploy semaphore to true in the gateway's deploy_config.
    """
    client = ctx.obj["client"]

    updates = {"trigger_deploy": True}

    try:
        result = update_gateway_deploy_config(client, gateway_name, updates)
        print_success(f"Point deployment triggered on gateway '{gateway_name}'")

        # Show deployment status
        deploy_config = result.get("deploy_config", {})
        click.echo(f"Last deploy: {deploy_config.get('last_deploy', 'Never')}")

    except click.ClickException:
        raise
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        ctx.exit(1)


@click.command("enable-bacnet")
@click.argument("gateway_name")
@click.pass_context
def enable_bacnet(ctx: click.Context, gateway_name: str) -> None:
    """Enable BACnet on the gateway.
    
    This sets the deploy_bacnet semaphore to true in the gateway's deploy_config.
    """
    client = ctx.obj["client"]

    updates = {"deploy_bacnet": True}

    try:
        update_gateway_deploy_config(client, gateway_name, updates)
        print_success(f"BACnet enabled on gateway '{gateway_name}'")

    except click.ClickException:
        raise
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        ctx.exit(1)


@click.command("disable-bacnet")
@click.argument("gateway_name")
@click.pass_context
def disable_bacnet(ctx: click.Context, gateway_name: str) -> None:
    """Disable BACnet on the gateway.
    
    This sets the deploy_bacnet semaphore to false in the gateway's deploy_config.
    """
    client = ctx.obj["client"]

    updates = {"deploy_bacnet": False}

    try:
        update_gateway_deploy_config(client, gateway_name, updates)
        print_success(f"BACnet disabled on gateway '{gateway_name}'")

    except click.ClickException:
        raise
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        ctx.exit(1)


@click.command("bacnet-status")
@click.argument("gateway_name")
@click.option("-o", "--output", type=click.Choice(["table", "json"]), default="table")
@click.pass_context
def bacnet_status(ctx: click.Context, gateway_name: str, output: str) -> None:
    """Show BACnet configuration status for a gateway."""
    client = ctx.obj["client"]

    try:
        if gateway_name is None:
            click.echo("Error: Gateway name cannot be None")
            ctx.exit(1)
        gateway = client.get_gateway(gateway_name)
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
                "bacnet_scan_object_id": deploy_config.get("bacnet_scan_object_id"),
                "bacnet_proxy_object_id": deploy_config.get("bacnet_proxy_object_id"),
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
            click.echo()

            click.echo("Object IDs:")
            click.echo(f"  Scan Object ID: {deploy_config.get('bacnet_scan_object_id', 'Not configured')}")
            click.echo(f"  Proxy Object ID: {deploy_config.get('bacnet_proxy_object_id', 'Not configured')}")
            click.echo()

            click.echo("History:")
            click.echo(f"  Last Scan: {deploy_config.get('last_scan', 'Never')}")
            click.echo(f"  Last Deploy: {deploy_config.get('last_deploy', 'Never')}")

    except APIError as e:
        print_error(f"Failed to get gateway status: {get_api_error_detail(e)}")
        ctx.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        ctx.exit(1)
