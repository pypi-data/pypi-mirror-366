"""
Utility functions for COESI CLI.

This module contains helper functions for Docker operations, IP validation,
environment file management, and other common tasks.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    import docker
else:
    try:
        import docker
    except ImportError:
        docker = None

from rich.console import Console

console = Console()


def validate_ip(ip: str) -> bool:
    """
    Validate IP address format and ranges.

    Args:
        ip: IP address string to validate

    Returns:
        True if valid, False otherwise
    """
    # Allow localhost and 127.0.0.1 for development
    if ip in ("localhost", "127.0.0.1"):
        return True

    # Validate IPv4 format
    ipv4_pattern = r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$"
    match = re.match(ipv4_pattern, ip)

    if not match:
        console.print(
            f"[red]Error:[/red] Invalid IP address format '{ip}'. Expected format: xxx.xxx.xxx.xxx"
        )
        return False

    # Check each octet is between 0-255
    octets = [int(x) for x in match.groups()]

    for octet in octets:
        if octet > 255 or octet < 0:
            console.print(
                f"[red]Error:[/red] Invalid IP address '{ip}'. Each octet must be between 0-255."
            )
            return False

    # Check for reserved/invalid ranges
    if octets[0] == 0 or octets[0] == 127 or octets[0] > 223:
        console.print(
            f"[red]Error:[/red] Invalid IP address '{ip}'. IP appears to be in a reserved range."
        )
        return False

    return True


def check_docker() -> bool:
    """
    Check if Docker and Docker Compose are available and running.

    Returns:
        True if Docker is ready, False otherwise
    """
    try:
        # Check if docker command is available
        subprocess.run(
            ["docker", "--version"], capture_output=True, check=True, timeout=10
        )
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        console.print("[red]Error:[/red] Docker is not installed or not in PATH")
        return False

    try:
        # Check if Docker daemon is running
        subprocess.run(["docker", "info"], capture_output=True, check=True, timeout=10)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        console.print("[red]Error:[/red] Docker daemon is not running")
        return False

    try:
        # Check if docker-compose command is available
        subprocess.run(
            ["docker-compose", "--version"], capture_output=True, check=True, timeout=10
        )
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        console.print(
            "[red]Error:[/red] Docker Compose is not installed or not in PATH"
        )
        return False

    return True


def validate_env(env_file: str) -> bool:
    """
    Validate environment file exists and has required variables.

    Args:
        env_file: Path to environment file

    Returns:
        True if valid, False otherwise
    """
    if not os.path.exists(env_file):
        console.print(f"[red]Error:[/red] Environment file {env_file} not found")
        return False

    # Check if required variables are present
    required_vars = [
        "DEPLOY_IP",
        "GRAPHDB_PORT",
        "CORE_API_PORT",
        "MODELS_MANAGER_PORT",
        "VALIDATION_ENGINE_PORT",
        "SCENARIO_MANAGER_PORT",
        "REACT_DASHBOARD_PORT",
    ]

    try:
        with open(env_file, "r") as f:
            content = f.read()

        for var in required_vars:
            if f"{var}=" not in content:
                console.print(
                    f"[yellow]Warning:[/yellow] Required variable {var} not found in {env_file}"
                )
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to read {env_file}: {e}")
        return False

    return True


def update_env_file(env_file: str, key: str, value: str) -> None:
    """
    Update a key-value pair in an environment file.

    Args:
        env_file: Path to environment file
        key: Environment variable key
        value: New value

    Raises:
        Exception: If file operations fail
    """
    if not os.path.exists(env_file):
        # Create file if it doesn't exist
        with open(env_file, "w") as f:
            f.write(f"{key}={value}\n")
        return

    # Read current content
    with open(env_file, "r") as f:
        lines = f.readlines()

    # Update or add the key-value pair
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            updated = True
            break

    if not updated:
        lines.append(f"{key}={value}\n")

    # Write back to file
    with open(env_file, "w") as f:
        f.writelines(lines)


class DockerComposeManager:
    """Manager class for Docker Compose operations."""

    def __init__(self, compose_file: str = "docker-compose.yml"):
        """
        Initialize Docker Compose manager.

        Args:
            compose_file: Path to docker-compose.yml file
        """
        self.compose_file = compose_file

    def _run_command(
        self, args: List[str], capture_output: bool = False
    ) -> Optional[str]:
        """
        Run docker-compose command.

        Args:
            args: Command arguments
            capture_output: Whether to capture output

        Returns:
            Command output if capture_output=True, None otherwise

        Raises:
            subprocess.CalledProcessError: If command fails
        """
        cmd = ["docker-compose"] + args

        if capture_output:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        else:
            subprocess.run(cmd, check=True)
            return None

    def up(self, profile: str, build: bool = False, detach: bool = False) -> None:
        """
        Start services with docker-compose up.

        Args:
            profile: Docker compose profile (dev/prod)
            build: Whether to build images
            detach: Whether to run in detached mode
        """
        args = ["--profile", profile, "up"]

        if build:
            args.append("--build")
        if detach:
            args.append("-d")

        self._run_command(args)

    def down(
        self, profile: str, volumes: bool = False, remove_orphans: bool = False
    ) -> None:
        """
        Stop and remove services with docker-compose down.

        Args:
            profile: Docker compose profile (dev/prod)
            volumes: Whether to remove volumes
            remove_orphans: Whether to remove orphan containers
        """
        args = ["--profile", profile, "down"]

        if volumes:
            args.append("-v")
        if remove_orphans:
            args.append("--remove-orphans")

        self._run_command(args)

    def restart(self, profile: str) -> None:
        """
        Restart services.

        Args:
            profile: Docker compose profile (dev/prod)
        """
        args = ["--profile", profile, "restart"]
        self._run_command(args)

    def ps(self, profile: str) -> None:
        """
        Show running services.

        Args:
            profile: Docker compose profile (dev/prod)
        """
        args = ["--profile", profile, "ps"]
        self._run_command(args)

    def logs(self, service: Optional[str] = None, follow: bool = False) -> None:
        """
        View logs for services.

        Args:
            service: Specific service name (optional)
            follow: Whether to follow logs
        """
        args = ["logs"]

        if follow:
            args.append("-f")
        if service:
            args.append(service)

        self._run_command(args)


def find_project_root() -> Optional[Path]:
    """
    Find the project root directory by looking for docker-compose.yml.

    Returns:
        Path to project root or None if not found
    """
    current = Path.cwd()

    while current != current.parent:
        if (current / "docker-compose.yml").exists():
            return current
        current = current.parent

    return None


def ensure_project_directory() -> Path:
    """
    Ensure we're in or can find the project directory.

    Returns:
        Path to project directory

    Raises:
        SystemExit: If project directory cannot be found
    """
    project_root = find_project_root()

    if project_root is None:
        console.print("[red]Error:[/red] Could not find docker-compose.yml file.")
        console.print("Please run this command from the COESI project directory.")
        sys.exit(1)

    # Change to project directory
    os.chdir(project_root)
    return project_root
