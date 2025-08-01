"""
AWS commands for tfmate.
"""

import fnmatch
import json
import sys

import botocore.session
import click
from rich.table import Table

from ..models.aws import AWSService
from .main import cli, console, create_progress, print_error, print_info


@cli.group()
def aws():
    """
    AWS-related commands for service discovery and analysis.
    """


@aws.command("services")
@click.option(
    "--names-only", is_flag=True, help="Output only service names in JSON format"
)
@click.option(
    "--filter-name", "-f", help="Filter services by name pattern (supports wildcards)"
)
@click.option(
    "--sort-by",
    type=click.Choice(["name", "service_id", "api_version"]),
    default="name",
    help="Sort services by field",
)
@click.pass_context
def list_aws_services(  # noqa: PLR0912
    ctx: click.Context, names_only: bool, filter_name: str | None, sort_by: str
):
    """
    List all available AWS services from botocore definitions.

    Provides a comprehensive list of AWS services with their metadata,
    including service IDs, API versions, and documentation URLs.
    """
    output_format = ctx.obj.get("output", "table")
    verbose = ctx.obj.get("verbose", False)

    try:
        with create_progress() as progress:
            task = progress.add_task("Loading AWS services...", total=None)

            # No credentials needed - just reading local botocore files
            session = botocore.session.get_session()
            services = []

            for service_name in session.get_available_services():
                service_model = session.get_service_model(service_name)
                services.append(
                    AWSService(
                        name=service_name,
                        service_id=service_model.metadata["serviceId"],
                        api_version=service_model.api_version,
                        endpoints=[service_model.endpoint_prefix],
                        documentation_url=service_model.metadata.get(
                            "documentationUrl"
                        ),
                    )
                )

            progress.update(task, description="Processing services...")

            # Apply filters if specified
            if filter_name:
                services = [
                    s
                    for s in services
                    if fnmatch.fnmatch(s.name.lower(), filter_name.lower())
                ]

            # Sort services
            services.sort(key=lambda s: getattr(s, sort_by))

            progress.update(task, description="Formatting output...")

        if names_only:
            result = {"services": [service.name for service in services]}
            if output_format == "json":
                click.echo(json.dumps(result, indent=2))
            else:
                # Even in table/text mode, names-only should be simple
                for service_name in result["services"]:
                    click.echo(service_name)
        else:
            if output_format == "json":
                click.echo(
                    json.dumps([service.model_dump() for service in services], indent=2)
                )
            elif output_format == "table":
                table = Table(
                    title="AWS Services", show_header=True, header_style="bold magenta"
                )
                table.add_column("Service Name", style="cyan", no_wrap=True)
                table.add_column("Service ID", style="magenta")
                table.add_column("API Version", style="green")
                table.add_column("Endpoints", style="yellow")

                if verbose:
                    table.add_column("Documentation", style="blue")

                for service in services:
                    row = [
                        service.name,
                        service.service_id,
                        service.api_version,
                        ", ".join(service.endpoints) if service.endpoints else "N/A",
                    ]
                    if verbose:
                        row.append(
                            str(service.documentation_url)
                            if service.documentation_url
                            else "N/A"
                        )
                    table.add_row(*row)

                console.print(table)
            else:  # text format
                for service in services:
                    click.echo(
                        f"{service.name}: {service.service_id} (v{service.api_version})"
                    )
                    if verbose and service.documentation_url:
                        click.echo(f"  Documentation: {service.documentation_url}")
                    click.echo()

            if verbose:
                print_info(f"Found {len(services)} AWS services")

    except Exception as e:
        print_error(
            f"Failed to load AWS services: {e}",
            [
                "Check that botocore is properly installed",
                "Verify network connectivity if downloading service definitions",
                "Try running with --verbose for more details",
            ],
        )
        raise
