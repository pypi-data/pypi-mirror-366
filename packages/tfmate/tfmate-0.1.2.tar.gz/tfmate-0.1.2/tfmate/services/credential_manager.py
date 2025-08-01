"""
Credential management service for tfmate.
"""

from typing import Any

import boto3

from ..exc import CredentialError
from ..models.terraform import StateAccessCredentials, TerraformConfig
from ..services.terraform_parser import TerraformParser


class CredentialManager:
    """
    Manages credentials for state file access
    """

    def __init__(self):
        """
        Initialize CredentialManager.
        """
        self.parser = TerraformParser()

    def detect_state_access_credentials(
        self, config: TerraformConfig, verbose: bool = False
    ) -> StateAccessCredentials:
        """
        Extract credentials needed for state file access from Terraform config.

        Args:
            config: Parsed Terraform configuration

        Returns:
            Credentials for state file access

        """
        # Check backend configuration first
        if config.terraform_block:
            backend_config = self.parser.extract_backend_config(config.terraform_block)
            if verbose:
                from rich.console import Console
                console = Console()
                console.print(f"[dim]DEBUG:[/dim] Found backend config: {backend_config.type}")

            if backend_config and backend_config.type == "s3":
                credentials = self.extract_s3_backend_credentials(backend_config.config)
                if verbose:
                    console.print(f"[dim]DEBUG:[/dim] Extracted S3 backend credentials: profile={credentials.profile}, region={credentials.region}")
                return credentials

        # Check AWS provider configuration as fallback
        aws_provider = self.find_aws_provider(config.providers)
        if aws_provider:
            if verbose:
                from rich.console import Console
                console = Console()
                console.print(f"[dim]DEBUG:[/dim] Using AWS provider credentials as fallback")
            return self.extract_provider_credentials(aws_provider)

        if verbose:
            from rich.console import Console
            console = Console()
            console.print(f"[dim]DEBUG:[/dim] No credentials found, using defaults")

        return StateAccessCredentials()

    def extract_s3_backend_credentials(
        self, config: dict[str, Any]
    ) -> StateAccessCredentials:
        """
        Extract credentials from S3 backend configuration.

        Args:
            config: S3 backend configuration dictionary

        Returns:
            Extracted credentials

        """
        return StateAccessCredentials(
            profile=config.get("profile"),
            region=config.get("region"),
            role_arn=config.get("assume_role", {}).get("role_arn"),
            assume_role_config=config.get("assume_role"),
        )

    def extract_provider_credentials(
        self, provider: dict[str, Any]
    ) -> StateAccessCredentials:
        """
        Extract credentials from AWS provider configuration.

        Args:
            provider: AWS provider configuration dictionary

        Returns:
            Extracted credentials

        """
        return StateAccessCredentials(
            profile=provider.get("profile"),
            region=provider.get("region"),
            role_arn=provider.get("assume_role", {}).get("role_arn"),
            assume_role_config=provider.get("assume_role"),
        )

    def find_aws_provider(
        self, providers: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """
        Find AWS provider configuration from provider list.

        Args:
            providers: List of provider configurations

        Returns:
            AWS provider configuration or None if not found

        """
        for provider in providers:
            if provider.get("name") == "aws":
                return provider
        return None

    def create_aws_session(self, credentials: StateAccessCredentials) -> boto3.Session:
        """
        Create boto3 session with specific credentials.

        Args:
            credentials: AWS credentials configuration

        Returns:
            Configured boto3 session

        Raises:
            CredentialError: If credential access fails

        """
        session_kwargs = {}

        if credentials.profile:
            session_kwargs["profile_name"] = credentials.profile
        if credentials.region:
            session_kwargs["region_name"] = credentials.region

        try:
            session = boto3.Session(**session_kwargs)

            # Handle assume role if specified
            if credentials.role_arn:
                sts = session.client("sts")
                assume_role_kwargs = {
                    "RoleArn": credentials.role_arn,
                    "RoleSessionName": "tfmate-state-access",
                }

                # Add additional assume role configuration if provided
                if credentials.assume_role_config:
                    assume_role_kwargs.update(credentials.assume_role_config)

                assumed_role = sts.assume_role(**assume_role_kwargs)

                session = boto3.Session(
                    aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
                    aws_secret_access_key=assumed_role["Credentials"][
                        "SecretAccessKey"
                    ],
                    aws_session_token=assumed_role["Credentials"]["SessionToken"],
                    region_name=credentials.region,
                )
        except Exception as e:
            suggestions = [
                "Check that AWS credentials are properly configured",
                "Verify the AWS profile exists and has correct permissions",
                "Ensure the role ARN is valid and accessible",
                "Check that the AWS region is valid",
            ]
            msg = f"Failed to create AWS session: {e}"
            raise CredentialError(msg, suggestions) from e
        else:
            return session

    def validate_credentials(self, credentials: StateAccessCredentials) -> bool:
        """
        Validate that credentials are properly configured.

        Args:
            credentials: Credentials to validate

        Returns:
            True if credentials are valid, False otherwise

        """
        try:
            session = self.create_aws_session(credentials)
            # Try to get caller identity to validate credentials
            sts = session.client("sts")
            sts.get_caller_identity()
        except Exception:  # noqa: BLE001
            return False
        return True
