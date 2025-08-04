#!/usr/bin/env python3
"""
CLI module for Pythonium.
"""

import asyncio
import importlib.metadata
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional, cast

import click
from rich.console import Console

__version__ = importlib.metadata.version("pythonium")

from .common.logging import get_logger, setup_logging
from .core.server import PythoniumMCPServer

console = Console()
logger = get_logger(__name__)


def print_banner():
    """Print the Pythonium banner."""
    banner = f"""
╔═══════════════════════════════════════╗
║             PYTHONIUM v{__version__:<10}         ║
║      Modular MCP Server for AI        ║
╚═══════════════════════════════════════╝
"""
    console.print(banner, style="bold blue")


@click.group()
@click.version_option(__version__, prog_name="Pythonium")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path",
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Logging level",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def main(ctx, config: Optional[Path], log_level: str, verbose: bool):
    """Pythonium - A modular MCP server for AI agents."""
    ctx.ensure_object(dict)

    # Setup logging
    setup_logging(level=log_level, verbose=verbose)

    # Store configuration path
    ctx.obj["config_path"] = config
    ctx.obj["log_level"] = log_level
    ctx.obj["verbose"] = verbose

    if verbose:
        print_banner()


@main.command()
@click.option("--host", default="localhost", help="Server host address")
@click.option("--port", default=8080, help="Server port number")
@click.option(
    "--transport",
    default="stdio",
    type=click.Choice(["stdio", "http", "websocket"]),
    help="Transport protocol",
)
@click.pass_context
def serve(ctx, host: str, port: int, transport: str):
    """Start the MCP server."""
    config_path = ctx.obj.get("config_path")
    log_level = ctx.obj.get("log_level", "INFO")

    # Set up logging first
    setup_logging(level=log_level)

    logger.info(f"Starting Pythonium MCP Server v{__version__}")
    logger.info(f"Transport: {transport}")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")

    try:
        # Create configuration overrides including logging level
        config_overrides = {
            "transport": {"type": transport, "host": host, "port": port},
            "logging": {"level": log_level.lower()},
        }

        # Create and start server with config overrides
        server = PythoniumMCPServer(
            config_file=config_path,
            config_overrides=config_overrides,
        )

        # For stdio transport, FastMCP manages its own event loop
        if transport.lower() == "stdio":
            # Run synchronously - FastMCP will handle the asyncio loop
            server.run_stdio()
        else:
            # For other transports, use async run method
            asyncio.run(server.run())

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


def _auto_detect_python_path(python_path: Optional[str]) -> str:
    """Auto-detect Python path if not provided."""
    if not python_path:
        python_path = sys.executable
        logger.debug(f"Auto-detected Python path: {python_path}")
    return python_path


def _auto_detect_pythonium_path(pythonium_path: Optional[str], python_path: str) -> str:
    """Auto-detect pythonium path if not provided."""
    if not pythonium_path:
        # Try to find pythonium module
        import pythonium

        pythonium_path = str(Path(pythonium.__file__).parent.parent)
        logger.debug(f"Auto-detected pythonium path: {pythonium_path}")
    return pythonium_path


def _build_mcp_config(python_path: str) -> dict:
    """Build MCP server configuration for pythonium."""
    return {
        "name": "pythonium",
        "command": [python_path, "-m", "pythonium", "serve"],
        "args": [
            "--log-level",
            "WARNING",
            "--transport",
            "stdio",
        ],
        "cwd": str(Path.home()),
        "auto_start": True,
        "description": "Pythonium MCP server for Python code analysis and execution",
    }


def _ensure_aixterm_config_exists(aixterm_config: Path) -> None:
    """Ensure aixterm config file exists, creating it if necessary."""
    if not aixterm_config.exists():
        logger.info(f"AIxTerm config not found at {aixterm_config}, initializing...")
        try:
            # Run aixterm --init-config to create the default config
            result = subprocess.run(
                ["aixterm", "--init-config"],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug(f"aixterm --init-config output: {result.stdout}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"Failed to initialize aixterm config: {e}")
            sys.exit(1)


def _load_aixterm_config(aixterm_config: Path) -> Dict[Any, Any]:
    """Load existing aixterm configuration."""
    try:
        with open(aixterm_config, "r") as f:
            aixterm_config_data = json.load(f)
        logger.debug(f"Loaded existing aixterm config from {aixterm_config}")
        return cast(Dict[Any, Any], aixterm_config_data)
    except Exception as e:
        logger.error(f"Could not load aixterm config: {e}")
        sys.exit(1)


def _update_aixterm_config(
    aixterm_config_data: dict, pythonium_mcp_config: dict
) -> dict:
    """Update aixterm config with pythonium MCP server configuration."""
    if "mcp_servers" not in aixterm_config_data:
        aixterm_config_data["mcp_servers"] = []

    # Remove any existing pythonium server config
    aixterm_config_data["mcp_servers"] = [
        server
        for server in aixterm_config_data["mcp_servers"]
        if server.get("name") != "pythonium"
    ]

    # Add new pythonium server config
    aixterm_config_data["mcp_servers"].append(pythonium_mcp_config)
    return aixterm_config_data


def _write_aixterm_config(aixterm_config: Path, aixterm_config_data: dict) -> None:
    """Write updated configuration to aixterm config file."""
    try:
        # Create backup if file exists
        if aixterm_config.exists():
            backup_path = aixterm_config.with_suffix(".backup")
            shutil.copy2(aixterm_config, backup_path)
            logger.debug(f"Created backup at {backup_path}")

        # Write new configuration
        with open(aixterm_config, "w") as f:
            json.dump(aixterm_config_data, f, indent=2)

        console.print("[bold green]Pythonium MCP server configured for aixterm")

    except Exception as e:
        logger.error(f"Failed to write configuration: {e}")
        sys.exit(1)


@main.command("configure-aixterm")
@click.option(
    "--aixterm-config",
    type=click.Path(path_type=Path),
    help="Path to aixterm configuration file (default: ~/.aixterm)",
)
@click.option(
    "--python-path",
    help="Python executable path for pythonium (auto-detected if not provided)",
)
@click.option(
    "--pythonium-path",
    help="Path to pythonium module (auto-detected if not provided)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be configured without making changes",
)
@click.pass_context
def configure_aixterm(
    ctx,
    aixterm_config: Optional[Path],
    python_path: Optional[str],
    pythonium_path: Optional[str],
    dry_run: bool,
):
    """Configure aixterm to use pythonium as an MCP server."""
    logger.info("Configuring aixterm to use pythonium...")

    # Determine aixterm config path - aixterm uses ~/.aixterm by default
    if not aixterm_config:
        aixterm_config = Path.home() / ".aixterm"

    # Auto-detect paths
    python_path = _auto_detect_python_path(python_path)
    pythonium_path = _auto_detect_pythonium_path(pythonium_path, python_path)

    # Build MCP server configuration
    pythonium_mcp_config = _build_mcp_config(python_path)

    # Ensure config exists and load it
    _ensure_aixterm_config_exists(aixterm_config)
    aixterm_config_data = _load_aixterm_config(aixterm_config)

    # Update configuration
    aixterm_config_data = _update_aixterm_config(
        aixterm_config_data, pythonium_mcp_config
    )

    if dry_run:
        console.print(
            "[bold yellow]DRY RUN - Configuration that would be written:[/bold yellow]"
        )
        console.print(json.dumps(aixterm_config_data, indent=2))
        console.print(f"\n[bold blue]Config file path:[/bold blue] {aixterm_config}")
        return

    # Write configuration
    _write_aixterm_config(aixterm_config, aixterm_config_data)


if __name__ == "__main__":
    main()
