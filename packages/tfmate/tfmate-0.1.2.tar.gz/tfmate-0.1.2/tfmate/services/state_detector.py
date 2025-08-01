"""
State file detection service for tfmate.
"""

from pathlib import Path
from typing import Any

from ..models.terraform import TerraformConfig, BackendConfig
from ..services.terraform_parser import TerraformParser


class StateDetector:
    """
    Detects state file location from Terraform configuration
    """

    def __init__(self):
        """
        Initialize StateDetector.
        """
        self.parser = TerraformParser()

    def detect_state_location(self, config: TerraformConfig, verbose: bool = False) -> BackendConfig:
        """
        Detect state file location from Terraform configuration.

        Args:
            config: Parsed Terraform configuration
            verbose: Enable verbose logging

        Returns:
            Backend configuration for state access
        """
        if not config.terraform_block:
            return BackendConfig(type="local", config={})

        return self.parser.extract_backend_config(config.terraform_block, verbose)

    def resolve_local_state(self, directory: Path) -> Path:
        """
        Resolve local state file path.

        Args:
            directory: Terraform directory

        Returns:
            Path to the local state file
        """
        return directory / "terraform.tfstate"

    def get_state_file_info(
        self, config: TerraformConfig, directory: Path
    ) -> dict[str, Any]:
        """
        Get comprehensive state file information.

        Args:
            config: Parsed Terraform configuration
            directory: Terraform directory

        Returns:
            Dictionary containing state file information
        """
        backend = self.detect_state_location(config)

        info = {
            "backend_type": backend.type,
            "backend_config": backend.config,
            "state_file_path": None,
            "requires_credentials": False,
        }

        if backend.type == "local":
            info["state_file_path"] = str(self.resolve_local_state(directory))
        elif backend.type == "s3":
            info["requires_credentials"] = True
            info["state_file_path"] = (
                f"s3://{backend.config.get('bucket')}/{backend.config.get('key')}"
            )
        elif backend.type == "http":
            info["state_file_path"] = backend.config.get("address")
        elif backend.type == "remote":
            info["requires_credentials"] = True
            info["state_file_path"] = (
                f"remote://{backend.config.get('hostname')}/{backend.config.get('organization')}"
            )

        return info
