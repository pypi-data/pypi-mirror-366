"""
Analysis commands for tfmate.
"""

import json
import sys
from pathlib import Path

import click
from rich.table import Table

from ..services.state_detector import StateDetector
from ..services.terraform_parser import TerraformParser
from .main import cli, console, create_progress, print_error, print_info, print_success


@cli.group()
def analyze():
    """
    Analysis commands for Terraform configurations and state files.
    """


@analyze.command("config")
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True),
    default=".",
    help="Terraform directory (default: current)",
)
@click.option("--show-providers", is_flag=True, help="Show provider configurations")
@click.option("--show-backend", is_flag=True, help="Show backend configuration")
@click.pass_context
def analyze_config(  # noqa: PLR0912
    ctx: click.Context, directory: str, show_providers: bool, show_backend: bool
):
    """
    Analyze Terraform configuration files.

    Provides detailed analysis of Terraform configuration files,
    including providers, backend configuration, and version constraints.
    """
    verbose = ctx.obj.get("verbose", False)
    output_format = ctx.obj.get("output", "table")

    try:
        directory_path = Path(directory)
        if verbose:
            print_info(
                f"Analyzing Terraform configuration in: {directory_path.absolute()}"
            )

        with create_progress() as progress:
            task = progress.add_task("Parsing Terraform files...", total=None)
            parser = TerraformParser()
            config = parser.parse_directory(directory_path)
            progress.update(task, description="Analyzing configuration...")

            detector = StateDetector()
            backend = detector.detect_state_location(config)
            progress.update(task, description="Formatting results...")

        # Prepare analysis results
        analysis = {
            "directory": str(directory_path.absolute()),
            "terraform_block": config.terraform_block is not None,
            "required_version": config.required_version,
            "backend_type": backend.type,
            "provider_count": len(config.providers),
            "providers": config.providers if show_providers else None,
            "backend_config": backend.config if show_backend else None,
        }

        # Output results
        if output_format == "json":
            # Clean up None values for JSON output
            json_output = {k: v for k, v in analysis.items() if v is not None}
            click.echo(json.dumps(json_output, indent=2))
        elif output_format == "table":
            table = Table(
                title="Terraform Configuration Analysis",
                show_header=True,
                header_style="bold magenta",
            )
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Directory", str(analysis["directory"]))
            table.add_row(
                "Terraform Block",
                "Present" if analysis["terraform_block"] else "Not found",
            )
            table.add_row(
                "Required Version", str(analysis["required_version"] or "Not specified")
            )
            table.add_row("Backend Type", str(analysis["backend_type"]))
            table.add_row("Provider Count", str(analysis["provider_count"]))

            console.print(table)

            # Show additional details if requested
            if show_providers and config.providers:
                provider_table = Table(
                    title="Provider Configurations",
                    show_header=True,
                    header_style="bold blue",
                )
                provider_table.add_column("Provider", style="cyan")
                provider_table.add_column("Configuration", style="yellow")

                for provider in config.providers:
                    provider_name = provider.get("name", "Unknown")
                    provider_config = str(provider.get("config", {}))
                    provider_table.add_row(provider_name, provider_config)

                console.print(provider_table)

            if show_backend and backend.config:
                backend_table = Table(
                    title="Backend Configuration",
                    show_header=True,
                    header_style="bold blue",
                )
                backend_table.add_column("Key", style="cyan")
                backend_table.add_column("Value", style="yellow")

                for key, value in backend.config.items():
                    # Mask sensitive values
                    _value = value
                    if (
                        "password" in key.lower()
                        or "token" in key.lower()
                        or "secret" in key.lower()
                    ):
                        _value = "***"
                    backend_table.add_row(key, str(_value))

                console.print(backend_table)
        else:  # text format
            click.echo(f"Configuration Analysis for: {analysis['directory']}")
            click.echo(
                f"Terraform Block: {'Present' if analysis['terraform_block'] else 'Not found'}"  # noqa: E501
            )
            click.echo(
                f"Required Version: {analysis['required_version'] or 'Not specified'}"
            )
            click.echo(f"Backend Type: {analysis['backend_type']}")
            click.echo(f"Provider Count: {analysis['provider_count']}")

            if show_providers and config.providers:
                click.echo("\nProvider Configurations:")
                for provider in config.providers:
                    click.echo(
                        f"  - {provider.get('name', 'Unknown')}: {provider.get('config', {})}"  # noqa: E501
                    )

            if show_backend and backend.config:
                click.echo("\nBackend Configuration:")
                for key, value in backend.config.items():
                    _value = value
                    if (
                        "password" in key.lower()
                        or "token" in key.lower()
                        or "secret" in key.lower()
                    ):
                        _value = "***"
                    click.echo(f"  - {key}: {_value}")

        if verbose:
            print_success(
                f"Successfully analyzed configuration in {analysis['directory']}"
            )

    except Exception as e:
        print_error(
            f"Failed to analyze configuration: {e}",
            [
                "Check that the directory contains valid Terraform files",
                "Verify file permissions",
                "Try running with --verbose for more details",
            ],
        )
        raise
