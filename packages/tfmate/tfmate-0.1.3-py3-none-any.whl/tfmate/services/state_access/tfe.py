"""
Terraform Enterprise state file access for tfmate.
"""

import json
from typing import Any

import requests

from ...models.terraform import StateAccessCredentials
from ...exc import StateFileError


def read_tfe_state(
    config: dict[str, Any], credentials: StateAccessCredentials
) -> dict[str, Any]:
    """
    Read state from Terraform Enterprise.

    Args:
        config: TFE backend configuration
        credentials: TFE credentials

    Returns:
        Parsed state file contents

    Raises:
        StateFileError: If TFE API request fails
        ValueError: If state file version is unsupported
    """
    session = requests.Session()
    hostname = config.get("hostname", "app.terraform.io")
    organization = config.get("organization")
    workspace = config.get("workspace")

    if not organization:
        raise StateFileError(
            "TFE backend",
            "Missing 'organization' configuration",
            [
                "Check that the TFE backend configuration includes an 'organization' field",
                "Verify the Terraform configuration is correct",
            ],
        )

    if not workspace:
        raise StateFileError(
            "TFE backend",
            "Missing 'workspace' configuration",
            [
                "Check that the TFE backend configuration includes a 'workspace' field",
                "Verify the Terraform configuration is correct",
            ],
        )

    # Configure authentication if token is provided
    if config.get("token"):
        session.headers.update(
            {
                "Authorization": f"Bearer {config['token']}",
                "Content-Type": "application/vnd.api+json",
            }
        )

    try:
        # Get workspace ID first
        workspace_id = get_tfe_workspace_id(config, session, organization, workspace)

        # Get current state version
        state_url = (
            f"https://{hostname}/api/v2/workspaces/{workspace_id}/current-state-version"
        )

        response = session.get(state_url, timeout=30)
        response.raise_for_status()

        state_data = response.json()

        if "data" not in state_data or "attributes" not in state_data["data"]:
            raise StateFileError(
                f"TFE workspace: {workspace}",
                "Invalid response format from TFE API",
                [
                    "Check that the TFE API is accessible",
                    "Verify the workspace exists and is accessible",
                ],
            )

        state = state_data["data"]["attributes"]["state"]

        # Validate Terraform 1.5+ format
        if state.get("version") != 4:
            raise ValueError(f"Unsupported state version: {state.get('version')}")

        return state
    except requests.exceptions.ConnectionError as e:
        suggestions = [
            "Check that TFE is accessible from your network",
            "Verify the hostname is correct",
            "Check network connectivity and firewall settings",
        ]
        raise StateFileError(
            f"TFE workspace: {workspace}", f"Connection error: {e}", suggestions
        )
    except requests.exceptions.Timeout as e:
        suggestions = [
            "Check that TFE is responding",
            "Verify network connectivity",
            "Try again later if TFE is experiencing issues",
        ]
        raise StateFileError(
            f"TFE workspace: {workspace}", f"Request timeout: {e}", suggestions
        )
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            suggestions = [
                "Check TFE token credentials",
                "Verify the token has access to the workspace",
                "Generate a new token if needed",
            ]
            raise StateFileError(
                f"TFE workspace: {workspace}", "Authentication failed", suggestions
            )
        elif response.status_code == 403:
            suggestions = [
                "Check that the token has permission to access the workspace",
                "Verify the workspace exists and is accessible",
                "Contact your TFE administrator",
            ]
            raise StateFileError(
                f"TFE workspace: {workspace}", "Access forbidden", suggestions
            )
        elif response.status_code == 404:
            suggestions = [
                "Check that the workspace name is correct",
                "Verify the workspace exists in the organization",
                "Check that the organization name is correct",
            ]
            raise StateFileError(
                f"TFE workspace: {workspace}", "Workspace not found", suggestions
            )
        else:
            suggestions = [
                "Check TFE service status",
                "Verify the API endpoint is correct",
                "Contact TFE support if the issue persists",
            ]
            raise StateFileError(
                f"TFE workspace: {workspace}",
                f"TFE API error {response.status_code}: {e}",
                suggestions,
            )
    except Exception as e:
        suggestions = [
            "Check network connectivity to TFE",
            "Verify TFE credentials and permissions",
            "Try running with --verbose for more details",
        ]
        raise StateFileError(
            f"TFE workspace: {workspace}", f"Unexpected error: {e}", suggestions
        )


def get_tfe_workspace_id(
    config: dict[str, Any], session: requests.Session, organization: str, workspace: str
) -> str:
    """
    Get TFE workspace ID from workspace name.

    Args:
        config: TFE backend configuration
        session: Configured requests session
        organization: TFE organization name
        workspace: TFE workspace name

    Returns:
        Workspace ID

    Raises:
        StateFileError: If workspace lookup fails
    """
    hostname = config.get("hostname", "app.terraform.io")
    workspace_url = (
        f"https://{hostname}/api/v2/organizations/{organization}/workspaces/{workspace}"
    )

    try:
        response = session.get(workspace_url, timeout=30)
        response.raise_for_status()

        workspace_data = response.json()

        if "data" not in workspace_data or "id" not in workspace_data["data"]:
            raise StateFileError(
                f"TFE workspace: {workspace}",
                "Invalid workspace response format",
                [
                    "Check that the workspace exists",
                    "Verify the organization and workspace names",
                ],
            )

        return workspace_data["data"]["id"]
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            suggestions = [
                "Check that the workspace name is correct",
                "Verify the workspace exists in the organization",
                "Check that the organization name is correct",
            ]
            raise StateFileError(
                f"TFE workspace: {workspace}", "Workspace not found", suggestions
            )
        else:
            suggestions = [
                "Check TFE service status",
                "Verify the API endpoint is correct",
                "Contact TFE support if the issue persists",
            ]
            raise StateFileError(
                f"TFE workspace: {workspace}",
                f"Failed to get workspace ID: {e}",
                suggestions,
            )
    except Exception as e:
        suggestions = [
            "Check network connectivity to TFE",
            "Verify TFE credentials and permissions",
            "Try running with --verbose for more details",
        ]
        raise StateFileError(
            f"TFE workspace: {workspace}",
            f"Failed to get workspace ID: {e}",
            suggestions,
        )
