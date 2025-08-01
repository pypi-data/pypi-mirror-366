"""
S3 state file access for tfmate.
"""

import json
from typing import Any

from botocore.exceptions import ClientError

from ...models.terraform import StateAccessCredentials
from ...exc import StateFileError
from ..credential_manager import CredentialManager


def read_s3_state(
    config: dict[str, Any], credentials: StateAccessCredentials, verbose: bool = False
) -> dict[str, Any]:
    """
    Read state from S3 using Terraform-configured credentials.

    Args:
        config: S3 backend configuration
        credentials: AWS credentials for access

    Returns:
        Parsed state file contents

    Raises:
        StateFileError: If state file access fails
        ValueError: If state file version is unsupported
    """
    credential_manager = CredentialManager()

    # Add verbose logging for session creation
    from rich.console import Console
    console = Console()

    def log_debug(message: str) -> None:
        """Log debug message if verbose mode is enabled"""
        if verbose:
            console.print(f"[dim]DEBUG:[/dim] {message}")

    log_debug(f"Creating AWS session with credentials: profile={credentials.profile}, region={credentials.region}, role_arn={credentials.role_arn}")

    session = credential_manager.create_aws_session(credentials)

    log_debug("AWS session created successfully")

    s3 = session.client("s3")

    log_debug("S3 client created successfully")

    bucket = config.get("bucket")
    key = config.get("key")
    state_location = f"s3://{bucket}/{key}"

    log_debug(f"Attempting S3 get_object: Bucket={bucket}, Key={key}")

    try:
        response = s3.get_object(Bucket=bucket, Key=key)

        log_debug("S3 get_object call successful")
        state_content = response["Body"].read().decode("utf-8")
        state = json.loads(state_content)

        # Validate Terraform 1.5+ format
        if state.get("version") != 4:
            raise ValueError(f"Unsupported state version: {state.get('version')}")

        return state
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchKey":
            suggestions = [
                "Check that the S3 bucket and key are correct",
                "Verify the state file exists in S3",
                "Run 'terraform init' to initialize the backend",
            ]
            raise StateFileError(
                state_location, "State file not found in S3", suggestions
            )
        elif error_code == "AccessDenied":
            suggestions = [
                "Check AWS credentials and permissions",
                "Verify the IAM role has S3 read access",
                "Check bucket policy and ACL settings",
            ]
            raise StateFileError(
                state_location,
                "Access denied - check AWS credentials and permissions",
                suggestions,
            )
        elif error_code == "NoSuchBucket":
            suggestions = [
                "Check that the S3 bucket name is correct",
                "Verify the bucket exists in the specified region",
                "Check AWS region configuration",
            ]
            raise StateFileError(
                state_location, f"S3 bucket not found: {bucket}", suggestions
            )
        else:
            suggestions = [
                "Check AWS credentials and permissions",
                "Verify network connectivity",
                "Check S3 service status",
            ]
            raise StateFileError(
                state_location,
                f"AWS error: {e.response['Error']['Message']}",
                suggestions,
            )
    except json.JSONDecodeError as e:
        suggestions = [
            "Check that the state file is valid JSON",
            "Verify the file is not corrupted",
            "Try running 'terraform state pull' to get a fresh state file",
        ]
        raise StateFileError(
            state_location, f"Invalid JSON in state file: {e}", suggestions
        )
    except Exception as e:
        suggestions = [
            "Check AWS credentials and permissions",
            "Verify network connectivity",
            "Try running with --verbose for more details",
        ]
        raise StateFileError(state_location, f"Unexpected error: {e}", suggestions)
