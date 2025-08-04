#!/usr/bin/env python3
"""
CmdRx CLI Interface

Main command line interface for the CmdRx tool.
"""

import sys
import subprocess
import os
from pathlib import Path
from typing import Optional, List
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .core import CmdRxCore
from .config import ConfigManager
from .exceptions import CmdRxError, ConfigurationError, LLMError

console = Console()

@click.command()
@click.argument('command', nargs=-1, required=False)
@click.option('--config', '-c', is_flag=True, help='Open configuration interface')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--version', is_flag=True, help='Show version and exit')
@click.option('--log-dir', type=click.Path(), help='Override default log directory')
@click.option('--dry-run', is_flag=True, help='Analyze without creating fix scripts')
def main(
    command: tuple,
    config: bool,
    verbose: bool,
    version: bool,
    log_dir: Optional[str],
    dry_run: bool
) -> None:
    """
    CmdRx - AI-powered command line troubleshooting tool.
    
    Usage:
        cmdrx systemctl status httpd    # Analyze command output
        systemctl status httpd | cmdrx  # Analyze piped input
        cmdrx --config                  # Open configuration
    """
    
    if version:
        from . import __version__
        click.echo(f"CmdRx version {__version__}")
        return
    
    if config:
        try:
            config_manager = ConfigManager()
            config_manager.run_tui()
        except ConfigurationError as e:
            console.print(f"[red]Configuration error: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            if verbose:
                console.print_exception()
            sys.exit(1)
        return
    
    try:
        # Initialize the core
        core = CmdRxCore(verbose=verbose, log_dir=log_dir, dry_run=dry_run)
        
        # Determine input mode
        if command:
            # Standalone mode - execute command and analyze output
            result = _execute_command_standalone(command, core, verbose)
        elif not sys.stdin.isatty():
            # Piped input mode
            result = _execute_command_piped(core, verbose)
        else:
            # No input provided
            console.print("[yellow]No command provided. Use --help for usage information.[/yellow]")
            ctx = click.get_current_context()
            click.echo(ctx.get_help())
            sys.exit(1)
        
        if result:
            console.print("\n[green]✓ Analysis complete. Check the output above and generated files.[/green]")
    
    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        console.print("[yellow]Run 'cmdrx --config' to set up configuration.[/yellow]")
        sys.exit(1)
    except LLMError as e:
        console.print(f"[red]LLM service error: {e}[/red]")
        sys.exit(1)
    except CmdRxError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


def _execute_command_standalone(command: tuple, core: CmdRxCore, verbose: bool) -> bool:
    """Execute a command in standalone mode and analyze its output."""
    cmd_str = ' '.join(command)
    
    if verbose:
        console.print(f"[blue]Executing command: {cmd_str}[/blue]")
    
    try:
        # Execute the command
        result = subprocess.run(
            cmd_str,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Prepare the full output (stdout + stderr)
        output_parts = []
        if result.stdout:
            output_parts.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output_parts.append(f"STDERR:\n{result.stderr}")
        
        command_output = "\n".join(output_parts) if output_parts else ""
        
        if not command_output.strip():
            console.print("[yellow]Command produced no output to analyze.[/yellow]")
            return False
        
        # Show the command output
        console.print(Panel(
            command_output,
            title=f"Command Output: {cmd_str}",
            border_style="blue"
        ))
        
        # Analyze with CmdRx
        return core.analyze_output(cmd_str, command_output, result.returncode)
        
    except subprocess.TimeoutExpired:
        raise CmdRxError(f"Command '{cmd_str}' timed out after 30 seconds")
    except subprocess.CalledProcessError as e:
        raise CmdRxError(f"Command '{cmd_str}' failed: {e}")


def _execute_command_piped(core: CmdRxCore, verbose: bool) -> bool:
    """Process piped input and analyze it."""
    if verbose:
        console.print("[blue]Reading from piped input...[/blue]")
    
    try:
        # Read all input from stdin
        piped_input = sys.stdin.read()
        
        if not piped_input.strip():
            console.print("[yellow]No input received from pipe.[/yellow]")
            return False
        
        # Show the piped input
        console.print(Panel(
            piped_input,
            title="Piped Input",
            border_style="blue"
        ))
        
        # Analyze with CmdRx (no original command or return code available)
        return core.analyze_output("<piped input>", piped_input, None)
        
    except Exception as e:
        raise CmdRxError(f"Failed to read piped input: {e}")


if __name__ == "__main__":
    main()