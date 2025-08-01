"""
Terraform configuration and state models for tfmate.
"""

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class TerraformConfig(BaseModel):
    """
    Represents a parsed Terraform configuration
    """

    #: The terraform block configuration
    terraform_block: dict | None = Field(
        None, description="Terraform block configuration"
    )
    #: List of provider configurations
    providers: list[dict] = Field(
        default_factory=list, description="Provider configurations"
    )
    #: Required Terraform version
    required_version: str | None = Field(None, description="Required Terraform version")

    @field_validator("required_version")
    @classmethod
    def validate_required_version(cls, v: str | None) -> str | None:
        """
        Validate required version format.

        Args:
            v: Required version string

        Returns:
            Validated version string

        Raises:
            ValueError: If version format is invalid

        """
        if v is not None:
            # Terraform version constraints like ">= 1.5.0", "~> 1.5", "1.5.0"
            if not re.match(r"^[~>=<!\s\d.]+$", v):
                msg = "Invalid Terraform version constraint format"
                raise ValueError(msg)
        return v


class BackendConfig(BaseModel):
    """
    Represents a Terraform backend configuration
    """

    #: The backend type (local, s3, http, remote)
    type: str = Field(..., description="Backend type")
    #: The backend configuration dictionary
    config: dict[str, Any] = Field(
        default_factory=dict, description="Backend configuration"
    )

    @field_validator("type")
    @classmethod
    def validate_backend_type(cls, v: str) -> str:
        """
        Validate backend type.

        Args:
            v: Backend type value

        Returns:
            Validated backend type

        Raises:
            ValueError: If backend type is invalid

        """
        valid_types = {"local", "s3", "http", "remote"}
        if v not in valid_types:
            msg = f"Backend type must be one of: {', '.join(valid_types)}"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_backend_config(self) -> "BackendConfig":
        """
        Validate backend configuration based on type.

        Returns:
            Self

        Raises:
            ValueError: If backend configuration is invalid

        """
        if self.type == "s3":
            required_keys = {"bucket", "key"}
            missing_keys = required_keys - set(self.config.keys())
            if missing_keys:
                msg = f"S3 backend requires keys: {', '.join(missing_keys)}"
                raise ValueError(msg)

            # Validate bucket name format
            bucket = self.config.get("bucket")
            if bucket and not re.match(r"^[a-z0-9][a-z0-9.-]*[a-z0-9]$", bucket):
                msg = "Invalid S3 bucket name format"
                raise ValueError(msg)

            # Validate region if present
            region = self.config.get("region")
            if region and not re.match(r"^[a-z]{2}-[a-z]+-\d+$", region):
                msg = "Invalid AWS region format"
                raise ValueError(msg)

        elif self.type == "http":
            if "address" not in self.config:
                msg = 'HTTP backend requires "address" key'
                raise ValueError(msg)

        elif self.type == "remote":
            required_keys = {"hostname", "organization"}
            missing_keys = required_keys - set(self.config.keys())
            if missing_keys:
                msg = f"Remote backend requires keys: {', '.join(missing_keys)}"
                raise ValueError(msg)

        return self


class StateAccessCredentials(BaseModel):
    """
    Represents credentials needed for state file access
    """

    #: AWS profile name
    profile: str | None = Field(None, description="AWS profile name")
    #: AWS region
    region: str | None = Field(None, description="AWS region")
    #: AWS role ARN for assume role
    role_arn: str | None = Field(None, description="AWS role ARN")
    #: Assume role configuration
    assume_role_config: dict | None = Field(
        None, description="Assume role configuration"
    )

    @field_validator("region")
    @classmethod
    def validate_region(cls, v: str | None) -> str | None:
        """
        Validate AWS region format.

        Args:
            v: AWS region value

        Returns:
            Validated region

        Raises:
            ValueError: If region format is invalid

        """
        if v is not None:
            if not re.match(r"^[a-z]{2}-[a-z]+-\d+$", v):
                msg = "Invalid AWS region format"
                raise ValueError(msg)
        return v

    @field_validator("role_arn")
    @classmethod
    def validate_role_arn(cls, v: str | None) -> str | None:
        """
        Validate AWS role ARN format.

        Args:
            v: Role ARN value

        Returns:
            Validated role ARN

        Raises:
            ValueError: If role ARN format is invalid

        """
        if v is not None:
            if not re.match(r"^arn:aws:iam::\d{12}:role/[a-zA-Z0-9+=,.@_-]+$", v):
                msg = "Invalid AWS role ARN format"
                raise ValueError(msg)
        return v


class TerraformState(BaseModel):
    """
    Represents a Terraform state file
    """

    #: State file version
    version: int = Field(
        ..., ge=4, description="State file version (must be >= 4 for Terraform 1.5+)"
    )
    #: Terraform version that created this state
    terraform_version: str = Field(..., min_length=1, description="Terraform version")
    #: State serial number
    serial: int = Field(..., ge=0, description="State serial number")
    #: State lineage identifier
    lineage: str = Field(..., min_length=1, description="State lineage identifier")
    #: State outputs
    outputs: dict = Field(default_factory=dict, description="State outputs")
    #: State resources
    resources: list[Any] = Field(default_factory=list, description="State resources")
    #: Check results (if any)
    check_results: Any | None = Field(None, description="Check results")

    @field_validator("terraform_version")
    @classmethod
    def validate_terraform_version(cls, v: str) -> str:
        """
        Validate Terraform version format.

        Args:
            v: Terraform version string

        Returns:
            Validated version string

        Raises:
            ValueError: If version format is invalid

        """
        # Terraform version format: x.y.z or x.y.z-dev
        if not re.match(r"^\d+\.\d+\.\d+(-dev)?$", v):
            msg = "Invalid Terraform version format"
            raise ValueError(msg)
        return v

    @field_validator("lineage")
    @classmethod
    def validate_lineage(cls, v: str) -> str:
        """
        Validate state lineage format.

        Args:
            v: Lineage string

        Returns:
            Validated lineage

        Raises:
            ValueError: If lineage format is invalid

        """
        # Lineage should be a UUID-like string
        if not re.match(
            r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$", v
        ):
            msg = "Invalid state lineage format (should be UUID-like)"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_state_file(self) -> "TerraformState":
        """
        Validate state file structure.

        Returns:
            Self

        Raises:
            ValueError: If state file structure is invalid

        """
        # Ensure we have at least one resource or output
        if not self.resources and not self.outputs:
            msg = "State file must contain at least one resource or output"
            raise ValueError(msg)

        return self
