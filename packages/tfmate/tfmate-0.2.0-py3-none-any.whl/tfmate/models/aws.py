"""
AWS service models for tfmate.
"""

import re

from pydantic import AnyUrl, BaseModel, Field, field_validator


class AWSService(BaseModel):
    """
    Describes an AWS service, e.g. ``ecs``
    """

    #: The name of the service
    name: str = Field(..., min_length=1, description="AWS service name")
    #: The id of the service
    service_id: str = Field(..., min_length=1, description="AWS service ID")
    #: The api version
    api_version: str = Field(..., min_length=1, description="AWS API version")
    #: A list of service endpoints
    endpoints: list[str] = Field(default_factory=list, description="Service endpoints")
    #: Where the service is documented
    documentation_url: AnyUrl | None = Field(
        None, description="Service documentation URL"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validate service name format.

        Args:
            v: Service name value

        Returns:
            Validated service name

        Raises:
            ValueError: If service name is invalid

        """
        if not v.isalnum() and not v.replace("-", "").isalnum():
            msg = "Service name must be alphanumeric with optional hyphens"
            raise ValueError(msg)
        return v.lower()

    @field_validator("api_version")
    @classmethod
    def validate_api_version(cls, v: str) -> str:
        """
        Validate API version format.

        Args:
            v: API version value

        Returns:
            Validated API version

        Raises:
            ValueError: If API version format is invalid

        """
        # API version should be in format like "2014-11-06"
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            msg = "API version must be in format YYYY-MM-DD"
            raise ValueError(msg)
        return v
