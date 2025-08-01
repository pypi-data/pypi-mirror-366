"""
HTTP state file access for tfmate.
"""

import json
from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from ...exc import StateFileError


def read_http_state(config: dict[str, Any]) -> dict[str, Any]:
    """
    Read state via HTTP.

    Args:
        config: HTTP backend configuration

    Returns:
        Parsed state file contents

    Raises:
        StateFileError: If HTTP request fails
        ValueError: If state file version is unsupported
    """
    session = requests.Session()
    address = config.get("address")

    if not address:
        raise StateFileError(
            "HTTP backend",
            "Missing 'address' configuration",
            [
                "Check that the HTTP backend configuration includes an 'address' field",
                "Verify the Terraform configuration is correct",
            ],
        )

    # Configure authentication if provided
    if config.get("username") and config.get("password"):
        session.auth = HTTPBasicAuth(config["username"], config["password"])

    try:
        response = session.get(address, timeout=30)
        response.raise_for_status()
        state = response.json()

        # Validate Terraform 1.5+ format
        if state.get("version") != 4:
            raise ValueError(f"Unsupported state version: {state.get('version')}")

        return state
    except requests.exceptions.ConnectionError as e:
        suggestions = [
            "Check that the HTTP server is running and accessible",
            "Verify the URL is correct",
            "Check network connectivity and firewall settings",
        ]
        raise StateFileError(address, f"Connection error: {e}", suggestions)
    except requests.exceptions.Timeout as e:
        suggestions = [
            "Check that the HTTP server is responding",
            "Verify network connectivity",
            "Try increasing the timeout if the server is slow",
        ]
        raise StateFileError(address, f"Request timeout: {e}", suggestions)
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            suggestions = [
                "Check username and password credentials",
                "Verify authentication configuration",
                "Check that credentials have access to the state file",
            ]
            raise StateFileError(address, "Authentication failed", suggestions)
        elif response.status_code == 403:
            suggestions = [
                "Check that the user has permission to access the state file",
                "Verify authentication credentials",
                "Contact the server administrator",
            ]
            raise StateFileError(address, "Access forbidden", suggestions)
        elif response.status_code == 404:
            suggestions = [
                "Check that the state file URL is correct",
                "Verify the state file exists on the server",
                "Run 'terraform init' to initialize the backend",
            ]
            raise StateFileError(address, "State file not found", suggestions)
        else:
            suggestions = [
                "Check the HTTP server status",
                "Verify the URL is correct",
                "Contact the server administrator",
            ]
            raise StateFileError(
                address, f"HTTP error {response.status_code}: {e}", suggestions
            )
    except json.JSONDecodeError as e:
        suggestions = [
            "Check that the server is returning valid JSON",
            "Verify the state file is not corrupted",
            "Check that the URL points to a Terraform state file",
        ]
        raise StateFileError(address, f"Invalid JSON response: {e}", suggestions)
    except Exception as e:
        suggestions = [
            "Check network connectivity",
            "Verify the HTTP server is accessible",
            "Try running with --verbose for more details",
        ]
        raise StateFileError(address, f"Unexpected error: {e}", suggestions)
