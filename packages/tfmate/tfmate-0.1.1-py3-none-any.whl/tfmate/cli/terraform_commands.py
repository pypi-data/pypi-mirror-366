"""
Terraform commands for tfmate.
"""

import json
import sys
from pathlib import Path

import click
from rich.table import Table

from ..exc import StateFileError
from ..services.credential_manager import CredentialManager
from ..services.state_access import (
    read_http_state,
    read_local_state,
    read_s3_state,
    read_tfe_state,
)
from ..services.state_detector import StateDetector
from ..services.terraform_parser import TerraformParser
from .main import cli, console, create_progress, print_error, print_info, print_success


@cli.group()
def terraform():
    """
    Terraform-specific commands for configuration and state analysis.
    """


@terraform.command("version")
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True),
    default=".",
    help="Terraform directory (default: current)",
)
@click.option(
    "--state-file",
    "-s",
    type=click.Path(exists=True),
    help="Explicit state file path (local only)",
)
@click.pass_context
def get_version(ctx: click.Context, directory: str, state_file: str | None):  # noqa: PLR0912, PLR0915
    """
    Get Terraform version from state file using Terraform-configured credentials.

    Analyzes the Terraform configuration to determine the backend type,
    extracts necessary credentials, and retrieves the Terraform version
    from the state file.
    """
    verbose = ctx.obj.get("verbose", False)
    output_format = ctx.obj.get("output", "table")

    try:
        if state_file:
            if verbose:
                print_info(f"Using explicit state file: {state_file}")

            with create_progress() as progress:
                task = progress.add_task("Reading state file...", total=None)
                state = read_local_state(Path(state_file))
                progress.update(task, description="Parsing state file...")

            version = state.get("terraform_version", "Unknown")

        else:
            directory_path = Path(directory)
            if verbose:
                print_info(
                    f"Analyzing Terraform configuration in: {directory_path.absolute()}"
                )

            with create_progress() as progress:
                task = progress.add_task(
                    "Parsing Terraform configuration...", total=None
                )
                parser = TerraformParser()
                config = parser.parse_directory(directory_path, verbose)

                if verbose:
                    print_info(f"Parsed {len(config.providers)} provider configurations")
                    if config.terraform_block:
                        print_info("Found terraform block in configuration")
                    else:
                        print_info("No terraform block found in configuration")

                progress.update(task, description="Detecting backend configuration...")

                detector = StateDetector()
                backend = detector.detect_state_location(config, verbose)

                if verbose:
                    print_info(f"Detected backend: {backend.type}")
                    if backend.config:
                        print_info(f"Backend config: {backend.config}")

                if backend.type == "s3":
                    progress.update(task, description="Extracting AWS credentials...")
                    credential_manager = CredentialManager()
                    credentials = credential_manager.detect_state_access_credentials(
                        config, verbose
                    )

                    if verbose:
                        print_info(f"Extracted credentials:")
                        if credentials.profile:
                            print_info(f"  - AWS profile: {credentials.profile}")
                        if credentials.region:
                            print_info(f"  - AWS region: {credentials.region}")
                        if credentials.role_arn:
                            print_info(f"  - Role ARN: {credentials.role_arn}")
                        if not credentials.profile and not credentials.region and not credentials.role_arn:
                            print_info("  - No specific credentials found, using default")

                    progress.update(task, description="Reading state from S3...")
                    if verbose:
                        bucket = backend.config.get("bucket")
                        key = backend.config.get("key")
                        print_info(f"Attempting to read state from s3://{bucket}/{key}")

                    state = read_s3_state(backend.config, credentials, verbose)

                elif backend.type == "http":
                    progress.update(task, description="Reading state via HTTP...")
                    state = read_http_state(backend.config)

                elif backend.type == "remote":
                    progress.update(
                        task, description="Reading state from Terraform Enterprise..."
                    )
                    credential_manager = CredentialManager()
                    credentials = credential_manager.detect_state_access_credentials(
                        config, verbose
                    )
                    state = read_tfe_state(backend.config, credentials)

                else:  # Local backend
                    progress.update(task, description="Reading local state file...")
                    state_path = detector.resolve_local_state(directory_path)
                    state = read_local_state(state_path)

            version = state.get("terraform_version", "Unknown")

        # Output the result
        if output_format == "json":
            result = {
                "terraform_version": version,
                "state_file": str(state_file) if state_file else "auto-detected",
                "backend_type": backend.type if not state_file else "local",
            }
            click.echo(json.dumps(result, indent=2))
        elif output_format == "table":
            table = Table(
                title="Terraform Version", show_header=True, header_style="bold magenta"
            )
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Terraform Version", version)
            table.add_row(
                "State File", str(state_file) if state_file else "Auto-detected"
            )
            if not state_file:
                table.add_row("Backend Type", backend.type)

            console.print(table)
        else:  # text format
            click.echo(f"Terraform version: {version}")
            if verbose:
                if state_file:
                    click.echo(f"State file: {state_file}")
                else:
                    click.echo(f"Backend type: {backend.type}")

        if verbose:
            print_success(f"Successfully retrieved Terraform version: {version}")

    except StateFileError as e:
        print_error(f"State file error: {e.reason}", e.suggestions)
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        print_error(
            f"Unexpected error: {e}",
            [
                "Check that you are logged in and have done 'aws sso login' if necessary",
                "Check that the Terraform configuration is valid",
                "Verify credentials and permissions for the backend",
                "Try running with --verbose for more details",
            ],
        )
        sys.exit(1)
