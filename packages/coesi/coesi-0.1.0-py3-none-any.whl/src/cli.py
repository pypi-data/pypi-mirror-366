#!/usr/bin/env python3
"""
COESI CLI - Main command line interface module.

This module provides the main CLI interface for managing COESI Platform
deployments. It replicates the functionality of the original deploy.sh
bash script in Python.
"""

import sys
import os
import subprocess
from typing import Optional, Dict, TYPE_CHECKING

import click
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    import docker
else:
    try:
        import docker
    except ImportError:
        docker = None
from dotenv import load_dotenv

from .utils import (
    validate_ip,
    check_docker,
    validate_env,
    update_env_file,
    DockerComposeManager,
)

console = Console()

# Default values
DEFAULT_DEV_IP = "localhost"
DEFAULT_PROD_IP = "192.168.177.23"


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version information")
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """
    COESI Platform CLI - Command line interface for managing Docker deployments.

    This tool allows you to deploy, manage, and monitor COESI Platform services
    in both development and production environments.
    """
    if version:
        from . import __version__

        click.echo(f"COESI CLI version {__version__}")
        return

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument("ip", required=False)
def dev(ip: Optional[str]) -> None:
    """
    Deploy development environment (localhost only).

    Development profile always uses localhost for security and consistency.
    No IP parameter is allowed for development deployments.
    """
    if ip:
        console.print(
            "[red]Error:[/red] Development profile does not accept IP parameter."
        )
        console.print("Development always uses localhost for security and consistency.")
        console.print("Usage: coesi dev")
        console.print("")
        console.print("For production with custom IP, use: coesi prod [IP_ADDRESS]")
        sys.exit(1)

    deploy_environment("dev", None)


@main.command()
@click.argument("ip", required=False)
def prod(ip: Optional[str]) -> None:
    """
    Deploy production environment with optional IP address.

    If no IP is provided, uses the default production IP.

    IP: Optional IP address for production deployment
    """
    if ip and not validate_ip(ip):
        console.print(f"[red]Error:[/red] Invalid IP address '{ip}'")
        console.print("Please provide a valid IP address for production deployment.")
        sys.exit(1)

    deploy_ip = ip or DEFAULT_PROD_IP
    deploy_environment("prod", deploy_ip)


@main.command()
@click.argument("profile", type=click.Choice(["dev", "prod"]), required=True)
def restart(profile: str) -> None:
    """
    Restart services without rebuilding.

    PROFILE: Environment profile (dev or prod)
    """
    restart_services(profile)


@main.command()
@click.argument(
    "profile", type=click.Choice(["dev", "prod", "all"]), required=False, default="all"
)
def stop(profile: str) -> None:
    """
    Stop services.

    PROFILE: Environment profile (dev, prod, or all)
    """
    stop_services(profile)


@main.command()
@click.argument(
    "profile", type=click.Choice(["dev", "prod", "all"]), required=False, default="all"
)
def status(profile: str) -> None:
    """
    Show service status.

    PROFILE: Environment profile (dev, prod, or all)
    """
    show_status(profile)


@main.command()
@click.argument("service", required=False)
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
def logs(service: Optional[str], follow: bool) -> None:
    """
    View logs for specific service or all services.

    SERVICE: Optional service name to view logs for
    """
    view_logs(service, follow)


@main.command()
@click.argument(
    "profile", type=click.Choice(["dev", "prod", "all"]), required=False, default="all"
)
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
def clean(profile: str, force: bool) -> None:
    """
    Remove containers and volumes.

    PROFILE: Environment profile (dev, prod, or all)
    """
    clean_environment(profile, force)


@main.command()
@click.argument("ip_address", required=True)
def ip(ip_address: str) -> None:
    """
    Change production IP in .env.prod file.

    IP_ADDRESS: New IP address for production environment
    """
    if not validate_ip(ip_address):
        console.print(f"[red]Error:[/red] Invalid IP address '{ip_address}'")
        console.print("Please provide a valid IP address.")
        sys.exit(1)

    env_file = ".env.prod"

    try:
        update_env_file(env_file, "DEPLOY_IP", ip_address)
        console.print(f"[green]Success:[/green] Production IP updated to: {ip_address}")
        console.print("Run 'coesi prod' to deploy with new IP")
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to update IP: {e}")
        sys.exit(1)


def deploy_environment(profile: str, ip: Optional[str], rebuild: bool = True) -> None:
    """Deploy environment with specified profile and IP."""
    # Validate Docker
    if not check_docker():
        console.print("[red]Error:[/red] Docker validation failed")
        sys.exit(1)

    # Set IP based on profile
    if profile == "dev":
        deploy_ip = "localhost"
    else:
        deploy_ip = ip or DEFAULT_PROD_IP

    # Set environment file
    env_file = f".env.{profile}"

    # Validate environment file
    if not validate_env(env_file):
        console.print(
            f"[red]Error:[/red] Environment file validation failed: {env_file}"
        )
        sys.exit(1)

    # Update IP if provided (only for prod)
    if ip and profile == "prod":
        update_env_file(env_file, "DEPLOY_IP", ip)

    # Load environment variables
    if os.path.exists(env_file):
        load_dotenv(env_file)

    console.print("[bold blue]=== Deploying COESI Platform ===[/bold blue]")
    console.print(f"Profile: {profile}")
    console.print(f"Deploy IP: {deploy_ip}")

    # Get port information from environment
    ports_info = get_port_info()
    console.print(
        f"Ports: GraphDB:{ports_info.get('GRAPHDB_PORT', 'N/A')}, "
        f"Core:{ports_info.get('CORE_API_PORT', 'N/A')}, "
        f"Models:{ports_info.get('MODELS_MANAGER_PORT', 'N/A')}"
    )
    console.print(
        f"       Validation:{ports_info.get('VALIDATION_ENGINE_PORT', 'N/A')}, "
        f"Scenarios:{ports_info.get('SCENARIO_MANAGER_PORT', 'N/A')}, "
        f"React:{ports_info.get('REACT_DASHBOARD_PORT', 'N/A')}"
    )
    console.print("")

    # Use DockerComposeManager for deployment
    manager = DockerComposeManager()

    try:
        # Stop existing containers
        console.print("Stopping existing containers...")
        manager.down(profile)

        # Build and start services
        if rebuild:
            console.print("Building and starting services...")
            manager.up(profile, build=True, detach=True)
        else:
            console.print("Starting services...")
            manager.up(profile, detach=True)

        # Show status
        console.print("")
        console.print("[bold blue]=== Deployment Status ===[/bold blue]")
        manager.ps(profile)

        # Show service URLs
        show_service_urls(deploy_ip, ports_info)

    except Exception as e:
        console.print(f"[red]Error during deployment:[/red] {e}")
        sys.exit(1)


def restart_services(profile: str) -> None:
    """Restart services without rebuilding."""
    if not check_docker():
        console.print("[red]Error:[/red] Docker validation failed")
        sys.exit(1)

    env_file = f".env.{profile}"
    if not validate_env(env_file):
        console.print(
            f"[red]Error:[/red] Environment file validation failed: {env_file}"
        )
        sys.exit(1)

    # Load environment variables
    if os.path.exists(env_file):
        load_dotenv(env_file)

    deploy_ip = os.getenv("DEPLOY_IP", "localhost")

    console.print(
        f"[bold blue]=== Restarting COESI Platform ({profile}) ===[/bold blue]"
    )
    console.print(f"Deploy IP: {deploy_ip}")
    console.print("")

    manager = DockerComposeManager()

    try:
        manager.restart(profile)
        console.print("")
        console.print("[bold blue]=== Restart Status ===[/bold blue]")
        manager.ps(profile)
    except Exception as e:
        console.print(f"[red]Error during restart:[/red] {e}")
        sys.exit(1)


def stop_services(profile: str) -> None:
    """Stop services."""
    if not check_docker():
        console.print("[red]Error:[/red] Docker validation failed")
        sys.exit(1)

    manager = DockerComposeManager()

    try:
        if profile == "all":
            console.print("Stopping all services...")
            manager.down("dev")
            manager.down("prod")
        else:
            console.print(f"Stopping {profile} services...")
            manager.down(profile)

        console.print("[green]Services stopped successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Error stopping services:[/red] {e}")
        sys.exit(1)


def show_status(profile: str) -> None:
    """Show status of services."""
    if not check_docker():
        console.print("[red]Error:[/red] Docker validation failed")
        sys.exit(1)

    manager = DockerComposeManager()

    try:
        if profile == "all":
            console.print("[bold blue]=== Development Services ===[/bold blue]")
            manager.ps("dev")
            console.print("")
            console.print("[bold blue]=== Production Services ===[/bold blue]")
            manager.ps("prod")
        else:
            console.print(f"[bold blue]=== {profile.title()} Services ===[/bold blue]")
            manager.ps(profile)
    except Exception as e:
        console.print(f"[red]Error getting status:[/red] {e}")
        sys.exit(1)


def view_logs(service: Optional[str], follow: bool = False) -> None:
    """View logs for services."""
    if not check_docker():
        console.print("[red]Error:[/red] Docker validation failed")
        sys.exit(1)

    manager = DockerComposeManager()

    try:
        if service:
            console.print(f"Showing logs for service: {service}")
        else:
            console.print("Showing logs for all services...")

        manager.logs(service, follow=follow)
    except Exception as e:
        console.print(f"[red]Error viewing logs:[/red] {e}")
        sys.exit(1)


def clean_environment(profile: str, force: bool = False) -> None:
    """Clean containers and volumes."""
    if not check_docker():
        console.print("[red]Error:[/red] Docker validation failed")
        sys.exit(1)

    manager = DockerComposeManager()

    try:
        if profile == "all":
            if not force:
                console.print("Cleaning all environments...")
                console.print("This will remove all containers, networks, and volumes.")
                if not click.confirm("Are you sure?"):
                    console.print("Clean operation cancelled.")
                    return

            manager.down("dev", volumes=True, remove_orphans=True)
            manager.down("prod", volumes=True, remove_orphans=True)

            # System prune
            try:
                subprocess.run(["docker", "system", "prune", "-f"], check=True)
            except subprocess.CalledProcessError:
                console.print(
                    "[yellow]Warning:[/yellow] Could not run docker system prune"
                )

            console.print("[green]All environments cleaned.[/green]")
        else:
            if not force:
                console.print(f"Cleaning {profile} environment...")
                console.print(
                    f"This will remove containers, networks, and volumes for {profile} profile."
                )
                if not click.confirm("Are you sure?"):
                    console.print("Clean operation cancelled.")
                    return

            manager.down(profile, volumes=True, remove_orphans=True)
            console.print(f"[green]{profile.title()} environment cleaned.[/green]")

    except Exception as e:
        console.print(f"[red]Error during cleanup:[/red] {e}")
        sys.exit(1)


def get_port_info() -> Dict[str, str]:
    """Get port information from environment variables."""
    return {
        "GRAPHDB_PORT": os.getenv("GRAPHDB_PORT", "7200"),
        "CORE_API_PORT": os.getenv("CORE_API_PORT", "8000"),
        "MODELS_MANAGER_PORT": os.getenv("MODELS_MANAGER_PORT", "8001"),
        "VALIDATION_ENGINE_PORT": os.getenv("VALIDATION_ENGINE_PORT", "8002"),
        "SCENARIO_MANAGER_PORT": os.getenv("SCENARIO_MANAGER_PORT", "8003"),
        "REACT_DASHBOARD_PORT": os.getenv("REACT_DASHBOARD_PORT", "3000"),
    }


def show_service_urls(deploy_ip: str, ports: Dict[str, str]) -> None:
    """Display service URLs in a formatted table."""
    console.print("")
    console.print("[bold blue]=== Services Available At ===[/bold blue]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Service", style="cyan")
    table.add_column("URL", style="green")

    services = [
        ("React Dashboard", f"http://{deploy_ip}:{ports['REACT_DASHBOARD_PORT']}"),
        ("GraphDB", f"http://{deploy_ip}:{ports['GRAPHDB_PORT']}"),
        ("Core API", f"http://{deploy_ip}:{ports['CORE_API_PORT']}"),
        ("Model Manager", f"http://{deploy_ip}:{ports['MODELS_MANAGER_PORT']}"),
        ("Validation", f"http://{deploy_ip}:{ports['VALIDATION_ENGINE_PORT']}"),
        ("Scenarios", f"http://{deploy_ip}:{ports['SCENARIO_MANAGER_PORT']}"),
    ]

    for service, url in services:
        table.add_row(service, url)

    console.print(table)


if __name__ == "__main__":
    main()
