"""
Local state file access for tfmate.
"""

import json
from pathlib import Path
from typing import Any

from ...exc import StateFileError


def read_local_state(path: Path) -> dict[str, Any]:
    """
    Read local state file.

    Args:
        path: Path to the state file

    Returns:
        Parsed state file contents

    Raises:
        StateFileError: If state file is invalid or not found
        ValueError: If state file version is unsupported
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)

        # Validate Terraform 1.5+ format
        if state.get("version") != 4:
            raise ValueError(f"Unsupported state version: {state.get('version')}")

        return state
    except json.JSONDecodeError as e:
        suggestions = [
            "Check that the state file is valid JSON",
            "Verify the file is not corrupted",
            "Try running 'terraform state pull' to get a fresh state file",
        ]
        raise StateFileError(str(path), f"Invalid JSON in state file: {e}", suggestions)
    except FileNotFoundError:
        suggestions = [
            "Check that the state file path is correct",
            "Run 'terraform init' if this is a new project",
            "Verify the file exists and is readable",
        ]
        raise StateFileError(str(path), "State file not found", suggestions)
    except Exception as e:
        suggestions = [
            "Check file permissions",
            "Verify the file is not locked by another process",
            "Try running with --verbose for more details",
        ]
        raise StateFileError(
            str(path), f"Unexpected error reading state file: {e}", suggestions
        )
