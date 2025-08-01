"""
Main CLI entry point for tfmate.
"""

import json
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..settings import Settings

console = Console()
stderr_console = Console(file=sys.stderr)


def create_progress() -> Progress:
    """
    Create a rich progress indicator for long-running operations.

    Returns:
        Configured progress indicator

    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=stderr_console,
    )


def print_error(message: str, suggestions: list[str] | None = None):
    """
    Print error message with optional suggestions.

    Args:
        message: Error message
        suggestions: List of suggestions to fix the error

    """
    error_panel = Panel(
        f"[red]{message}[/red]", title="[bold red]Error[/bold red]", border_style="red"
    )
    stderr_console.print(error_panel)

    if suggestions:
        stderr_console.print("\n[bold]Suggestions:[/bold]")
        for suggestion in suggestions:
            stderr_console.print(f"  • {suggestion}")


def print_success(message: str):
    """
    Print success message.

    Args:
        message: Success message

    """
    success_panel = Panel(
        f"[green]{message}[/green]",
        title="[bold green]Success[/bold green]",
        border_style="green",
    )
    stderr_console.print(success_panel)


def print_info(message: str):
    """
    Print informational message.

    Args:
        message: Informational message

    """
    info_panel = Panel(
        f"[blue]{message}[/blue]",
        title="[bold blue]Info[/bold blue]",
        border_style="blue",
    )
    stderr_console.print(info_panel)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress all output except errors")
@click.option(
    "--config-file", type=click.Path(exists=True), help="Custom configuration file path"
)
@click.option(
    "--output",
    type=click.Choice(["json", "table", "text"]),
    default="table",
    help="Output format",
)
@click.pass_context
def cli(
    ctx: click.Context, verbose: bool, quiet: bool, config_file: str | None, output: str
):
    """
    Terraform maintenance tool for Terraform 1.5+.

    A powerful CLI tool for analyzing Terraform configurations and state files,
    providing insights into your infrastructure as code.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Store global options in context
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    ctx.obj["output"] = output
    ctx.obj["config_file"] = config_file

    # Load settings
    try:
        settings = Settings.from_file(config_file) if config_file else Settings()
        ctx.obj["settings"] = settings
    except Exception as e:  # noqa: BLE001
        print_error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Configure console based on quiet mode
    if quiet:
        console.quiet = True


@cli.command("settings")
@click.pass_context
def show_settings(ctx: click.Context):
    """
    Settings-related commands.
    """
    output_format = ctx.obj.get("output", "table")
    verbose = ctx.obj.get("verbose", False)

    # Create a fresh Settings instance to avoid test state crossover
    # If a config file was specified, use it
    config_file = ctx.obj.get("config_file")
    if config_file:
        settings = Settings.from_file(config_file)
    else:
        settings = Settings()

    if output_format == "json":
        click.echo(json.dumps(settings.model_dump()))
    elif output_format == "table":
        table = Table(
            title="Settings", show_header=True, header_style="bold magenta"
        )
        table.add_column("Setting Name", style="cyan")
        table.add_column("Value", style="green")

        for setting_name, setting_value in settings.model_dump().items():
            table.add_row(setting_name, str(setting_value))

        console.print(table)
    else:  # text format
        for setting_name, setting_value in settings.model_dump().items():
            click.echo(f"{setting_name}: {setting_value}")
            click.echo()

    if verbose:
        print_info(f"Found {len(settings.model_dump())} settings")
