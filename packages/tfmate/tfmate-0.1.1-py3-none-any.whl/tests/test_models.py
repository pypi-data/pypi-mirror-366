"""
Unit tests for tfmate models.
"""

import pytest
from pydantic import ValidationError

from tfmate.models.aws import AWSService
from tfmate.models.terraform import (
    TerraformConfig,
    BackendConfig,
    StateAccessCredentials,
    TerraformState,
)


class TestAWSService:
    """Test AWS service model validation."""

    def test_valid_service(self):
        """Test valid AWS service creation."""
        service = AWSService(
            name="ecs",
            service_id="Amazon Elastic Container Service",
            api_version="2014-11-13",
            endpoints=["ecs"],
        )
        assert service.name == "ecs"  # Should be lowercased
        assert service.service_id == "Amazon Elastic Container Service"
        assert service.api_version == "2014-11-13"
        assert service.endpoints == ["ecs"]

    def test_invalid_service_name(self):
        """Test invalid service name raises error."""
        with pytest.raises(ValidationError) as exc_info:
            AWSService(
                name="invalid@service",
                service_id="Test Service",
                api_version="2014-11-13",
                endpoints=["test"],
            )
        assert "Service name must be alphanumeric" in str(exc_info.value)

    def test_invalid_api_version(self):
        """Test invalid API version raises error."""
        with pytest.raises(ValidationError) as exc_info:
            AWSService(
                name="ecs",
                service_id="Test Service",
                api_version="invalid-version",
                endpoints=["test"],
            )
        assert "API version must be in format YYYY-MM-DD" in str(exc_info.value)

    def test_service_name_normalization(self):
        """Test service name is normalized to lowercase."""
        service = AWSService(
            name="ECS",
            service_id="Test Service",
            api_version="2014-11-13",
            endpoints=["test"],
        )
        assert service.name == "ecs"


class TestTerraformConfig:
    """Test Terraform configuration model."""

    def test_valid_config(self):
        """Test valid Terraform configuration."""
        config = TerraformConfig(
            terraform_block={"required_version": ">= 1.5.0"},
            providers=[{"name": "aws", "region": "us-west-2"}],
            required_version=">= 1.5.0",
        )
        assert config.terraform_block == {"required_version": ">= 1.5.0"}
        assert len(config.providers) == 1
        assert config.required_version == ">= 1.5.0"

    def test_invalid_required_version(self):
        """Test invalid required version raises error."""
        with pytest.raises(ValidationError) as exc_info:
            TerraformConfig(required_version="invalid@version")
        assert "Invalid Terraform version constraint format" in str(exc_info.value)

    def test_empty_config(self):
        """Test empty configuration is valid."""
        config = TerraformConfig()
        assert config.terraform_block is None
        assert config.providers == []
        assert config.required_version is None


class TestBackendConfig:
    """Test backend configuration model."""

    def test_valid_local_backend(self):
        """Test valid local backend configuration."""
        backend = BackendConfig(type="local", config={})
        assert backend.type == "local"
        assert backend.config == {}

    def test_valid_s3_backend(self):
        """Test valid S3 backend configuration."""
        backend = BackendConfig(
            type="s3",
            config={
                "bucket": "my-terraform-state",
                "key": "prod/terraform.tfstate",
                "region": "us-west-2",
            },
        )
        assert backend.type == "s3"
        assert backend.config["bucket"] == "my-terraform-state"

    def test_invalid_backend_type(self):
        """Test invalid backend type raises error."""
        with pytest.raises(ValidationError) as exc_info:
            BackendConfig(type="invalid", config={})
        assert "Backend type must be one of" in str(exc_info.value)

    def test_s3_backend_missing_required_keys(self):
        """Test S3 backend missing required keys raises error."""
        with pytest.raises(ValidationError) as exc_info:
            BackendConfig(type="s3", config={"bucket": "test"})
        assert "S3 backend requires keys" in str(exc_info.value)

    def test_s3_backend_invalid_bucket_name(self):
        """Test S3 backend with invalid bucket name raises error."""
        with pytest.raises(ValidationError) as exc_info:
            BackendConfig(
                type="s3",
                config={"bucket": "invalid.bucket.name@", "key": "terraform.tfstate"},
            )
        assert "Invalid S3 bucket name format" in str(exc_info.value)

    def test_s3_backend_invalid_region(self):
        """Test S3 backend with invalid region raises error."""
        with pytest.raises(ValidationError) as exc_info:
            BackendConfig(
                type="s3",
                config={
                    "bucket": "my-terraform-state",
                    "key": "terraform.tfstate",
                    "region": "invalid-region",
                },
            )
        assert "Invalid AWS region format" in str(exc_info.value)

    def test_http_backend_missing_address(self):
        """Test HTTP backend missing address raises error."""
        with pytest.raises(ValidationError) as exc_info:
            BackendConfig(type="http", config={})
        assert 'HTTP backend requires "address" key' in str(exc_info.value)

    def test_remote_backend_missing_keys(self):
        """Test remote backend missing required keys raises error."""
        with pytest.raises(ValidationError) as exc_info:
            BackendConfig(type="remote", config={"hostname": "app.terraform.io"})
        assert "Remote backend requires keys" in str(exc_info.value)


class TestStateAccessCredentials:
    """Test state access credentials model."""

    def test_valid_credentials(self):
        """Test valid credentials creation."""
        creds = StateAccessCredentials(
            profile="prod",
            region="us-west-2",
            role_arn="arn:aws:iam::123456789012:role/TerraformRole",
        )
        assert creds.profile == "prod"
        assert creds.region == "us-west-2"
        assert creds.role_arn == "arn:aws:iam::123456789012:role/TerraformRole"

    def test_invalid_region_format(self):
        """Test invalid region format raises error."""
        with pytest.raises(ValidationError) as exc_info:
            StateAccessCredentials(region="invalid-region")
        assert "Invalid AWS region format" in str(exc_info.value)

    def test_invalid_role_arn_format(self):
        """Test invalid role ARN format raises error."""
        with pytest.raises(ValidationError) as exc_info:
            StateAccessCredentials(role_arn="invalid-arn")
        assert "Invalid AWS role ARN format" in str(exc_info.value)

    def test_empty_credentials(self):
        """Test empty credentials are valid."""
        creds = StateAccessCredentials()
        assert creds.profile is None
        assert creds.region is None
        assert creds.role_arn is None


class TestTerraformState:
    """Test Terraform state model."""

    def test_valid_state(self):
        """Test valid state creation."""
        state = TerraformState(
            version=4,
            terraform_version="1.5.0",
            serial=1,
            lineage="12345678-1234-1234-1234-123456789012",
            outputs={"test": {"value": "test"}},
            resources=[],
        )
        assert state.version == 4
        assert state.terraform_version == "1.5.0"
        assert state.serial == 1
        assert state.lineage == "12345678-1234-1234-1234-123456789012"

    def test_invalid_version_too_old(self):
        """Test invalid version (too old) raises error."""
        with pytest.raises(ValidationError) as exc_info:
            TerraformState(
                version=3,  # Too old for Terraform 1.5+
                terraform_version="1.5.0",
                serial=1,
                lineage="12345678-1234-1234-1234-123456789012",
                outputs={},
                resources=[],
            )
        assert "greater than or equal to 4" in str(exc_info.value)

    def test_invalid_terraform_version_format(self):
        """Test invalid Terraform version format raises error."""
        with pytest.raises(ValidationError) as exc_info:
            TerraformState(
                version=4,
                terraform_version="invalid-version",
                serial=1,
                lineage="12345678-1234-1234-1234-123456789012",
                outputs={},
                resources=[],
            )
        assert "Invalid Terraform version format" in str(exc_info.value)

    def test_invalid_lineage_format(self):
        """Test invalid lineage format raises error."""
        with pytest.raises(ValidationError) as exc_info:
            TerraformState(
                version=4,
                terraform_version="1.5.0",
                serial=1,
                lineage="invalid-lineage",
                outputs={},
                resources=[],
            )
        assert "Invalid state lineage format" in str(exc_info.value)

    def test_state_must_have_content(self):
        """Test state must have at least one resource or output."""
        with pytest.raises(ValidationError) as exc_info:
            TerraformState(
                version=4,
                terraform_version="1.5.0",
                serial=1,
                lineage="12345678-1234-1234-1234-123456789012",
                outputs={},
                resources=[],
            )
        assert "State file must contain at least one resource or output" in str(
            exc_info.value
        )

    def test_state_with_outputs_is_valid(self):
        """Test state with outputs is valid."""
        state = TerraformState(
            version=4,
            terraform_version="1.5.0",
            serial=1,
            lineage="12345678-1234-1234-1234-123456789012",
            outputs={"test": {"value": "test"}},
            resources=[],
        )
        assert state.outputs == {"test": {"value": "test"}}

    def test_state_with_resources_is_valid(self):
        """Test state with resources is valid."""
        state = TerraformState(
            version=4,
            terraform_version="1.5.0",
            serial=1,
            lineage="12345678-1234-1234-1234-123456789012",
            outputs={},
            resources=[{"type": "aws_instance", "name": "test"}],
        )
        assert len(state.resources) == 1
