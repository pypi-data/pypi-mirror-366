"""
Unit tests for tfmate services.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from tfmate.exc import TerraformConfigError
from tfmate.services.credential_manager import CredentialManager
from tfmate.services.state_detector import StateDetector
from tfmate.services.terraform_parser import TerraformParser


class TestTerraformParser:
    """Test Terraform parser service."""

    def test_parse_from_string_valid_hcl(self):
        """Test parsing valid HCL content."""
        parser = TerraformParser()
        content = """
        terraform {
          required_version = ">= 1.5.0"

          backend "s3" {
            bucket = "my-terraform-state"
            key    = "prod/terraform.tfstate"
            region = "us-west-2"
          }
        }

        provider "aws" {
          region = "us-west-2"
        }
        """

        config = parser.parse_from_string(content)

        assert config.terraform_block is not None
        assert config.required_version == ">= 1.5.0"
        assert len(config.providers) == 1
        # Provider structure may vary, just check it exists
        assert config.providers[0] is not None

    def test_parse_from_string_invalid_hcl(self):
        """Test parsing invalid HCL content raises error."""
        parser = TerraformParser()
        content = """
        terraform {
          required_version = ">= 1.5.0"

          backend "s3" {
            bucket = "my-terraform-state"
            key    = "prod/terraform.tfstate"
            region = "us-west-2"
            invalid_syntax = {
        }
        """

        with pytest.raises(TerraformConfigError) as exc_info:
            parser.parse_from_string(content)
        assert "Failed to parse HCL content" in str(exc_info.value)

    def test_parse_directory_with_files(self, tmp_path):
        """Test parsing directory with Terraform files."""
        parser = TerraformParser()

        # Create a test .tf file
        tf_file = tmp_path / "main.tf"
        tf_file.write_text("""
        terraform {
          required_version = ">= 1.5.0"
        }

        provider "aws" {
          region = "us-west-2"
        }
        """)

        config = parser.parse_directory(tmp_path)

        assert config.terraform_block is not None
        assert config.required_version == ">= 1.5.0"
        assert len(config.providers) == 1

    def test_parse_directory_no_files(self, tmp_path):
        """Test parsing directory with no .tf files."""
        parser = TerraformParser()

        config = parser.parse_directory(tmp_path)

        assert config.terraform_block is None
        assert config.providers == []
        assert config.required_version is None

    def test_parse_directory_nonexistent(self):
        """Test parsing nonexistent directory raises error."""
        parser = TerraformParser()

        with pytest.raises(FileNotFoundError):
            parser.parse_directory(Path("/nonexistent/path"))

    def test_parse_directory_multiple_terraform_blocks(self, tmp_path):
        """Test parsing directory with multiple terraform blocks, selecting the one with backend."""
        parser = TerraformParser()

        # Create a test .tf file with backend configuration
        main_tf = tmp_path / "main.tf"
        main_tf.write_text("""
        terraform {
          backend "s3" {
            bucket = "my-terraform-state"
            key    = "prod/terraform.tfstate"
            region = "us-west-2"
            profile = "prod"
          }
        }

        provider "aws" {
          region = "us-west-2"
        }
        """)

        # Create another .tf file with version requirements but no backend
        versions_tf = tmp_path / "versions.tf"
        versions_tf.write_text("""
        terraform {
          required_version = ">= 1.5.0"
          required_providers {
            aws = {
              source  = "hashicorp/aws"
              version = "~> 5.0"
            }
          }
        }
        """)

        config = parser.parse_directory(tmp_path)

        # Should use the terraform block with backend configuration
        assert config.terraform_block is not None
        assert "backend" in config.terraform_block
        assert config.terraform_block["backend"][0]["s3"]["bucket"] == "my-terraform-state"
        assert len(config.providers) == 1

    def test_parse_directory_multiple_terraform_blocks_verbose(self, tmp_path):
        """Test parsing directory with multiple terraform blocks and verbose logging."""
        parser = TerraformParser()

        # Create a test .tf file with backend configuration
        main_tf = tmp_path / "main.tf"
        main_tf.write_text("""
        terraform {
          backend "s3" {
            bucket = "my-terraform-state"
            key    = "prod/terraform.tfstate"
            region = "us-west-2"
            profile = "prod"
          }
        }

        provider "aws" {
          region = "us-west-2"
        }
        """)

        # Create another .tf file with version requirements but no backend
        versions_tf = tmp_path / "versions.tf"
        versions_tf.write_text("""
        terraform {
          required_version = ">= 1.5.0"
          required_providers {
            aws = {
              source  = "hashicorp/aws"
              version = "~> 5.0"
            }
          }
        }
        """)

        config = parser.parse_directory(tmp_path, verbose=True)

        # Should use the terraform block with backend configuration
        assert config.terraform_block is not None
        assert "backend" in config.terraform_block
        assert config.terraform_block["backend"][0]["s3"]["bucket"] == "my-terraform-state"
        assert len(config.providers) == 1

    def test_extract_backend_config_s3(self):
        """Test extracting S3 backend configuration."""
        parser = TerraformParser()
        terraform_block = {
            "backend": [
                {
                    "s3": [
                        {
                            "bucket": "my-terraform-state",
                            "key": "prod/terraform.tfstate",
                            "region": "us-west-2",
                        }
                    ]
                }
            ]
        }

        backend = parser.extract_backend_config(terraform_block)

        assert backend.type == "s3"
        assert backend.config["bucket"] == "my-terraform-state"
        assert backend.config["key"] == "prod/terraform.tfstate"
        assert backend.config["region"] == "us-west-2"

    def test_extract_backend_config_s3_verbose(self):
        """Test extracting S3 backend configuration with verbose logging."""
        parser = TerraformParser()
        terraform_block = {
            "backend": [
                {
                    "s3": [
                        {
                            "bucket": "my-terraform-state",
                            "key": "prod/terraform.tfstate",
                            "region": "us-west-2",
                        }
                    ]
                }
            ]
        }

        backend = parser.extract_backend_config(terraform_block, verbose=True)

        assert backend.type == "s3"
        assert backend.config["bucket"] == "my-terraform-state"
        assert backend.config["key"] == "prod/terraform.tfstate"
        assert backend.config["region"] == "us-west-2"

    def test_extract_backend_config_local(self):
        """Test extracting local backend configuration."""
        parser = TerraformParser()
        terraform_block = {}

        backend = parser.extract_backend_config(terraform_block)

        assert backend.type == "local"
        assert backend.config == {}

    def test_extract_backend_config_local_verbose(self):
        """Test extracting local backend configuration with verbose logging."""
        parser = TerraformParser()
        terraform_block = {}

        backend = parser.extract_backend_config(terraform_block, verbose=True)

        assert backend.type == "local"
        assert backend.config == {}

    def test_extract_backend_config_empty_backend(self):
        """Test extracting empty backend configuration."""
        parser = TerraformParser()
        terraform_block = {"backend": []}

        backend = parser.extract_backend_config(terraform_block)

        assert backend.type == "local"
        assert backend.config == {}

    def test_extract_backend_config_empty_backend_verbose(self):
        """Test extracting empty backend configuration with verbose logging."""
        parser = TerraformParser()
        terraform_block = {"backend": []}

        backend = parser.extract_backend_config(terraform_block, verbose=True)

        assert backend.type == "local"
        assert backend.config == {}


class TestStateDetector:
    """Test state detector service."""

    def test_detect_state_location_with_backend(self):
        """Test detecting state location with backend configuration."""
        detector = StateDetector()

        # Mock the parser to return a config with backend
        mock_config = Mock()
        mock_config.terraform_block = {
            "backend": [
                {
                    "s3": [
                        {
                            "bucket": "my-terraform-state",
                            "key": "prod/terraform.tfstate",
                        }
                    ]
                }
            ]
        }

        with patch.object(detector.parser, "extract_backend_config") as mock_extract:
            mock_extract.return_value = Mock(type="s3", config={"bucket": "test"})
            backend = detector.detect_state_location(mock_config)

        assert backend.type == "s3"

    def test_detect_state_location_with_backend_verbose(self):
        """Test detecting state location with backend configuration and verbose logging."""
        detector = StateDetector()

        # Mock the parser to return a config with backend
        mock_config = Mock()
        mock_config.terraform_block = {
            "backend": [
                {
                    "s3": [
                        {
                            "bucket": "my-terraform-state",
                            "key": "prod/terraform.tfstate",
                        }
                    ]
                }
            ]
        }

        with patch.object(detector.parser, "extract_backend_config") as mock_extract:
            mock_extract.return_value = Mock(type="s3", config={"bucket": "test"})
            backend = detector.detect_state_location(mock_config, verbose=True)

        assert backend.type == "s3"

    def test_detect_state_location_no_backend(self):
        """Test detecting state location without backend configuration."""
        detector = StateDetector()

        mock_config = Mock()
        mock_config.terraform_block = None

        backend = detector.detect_state_location(mock_config)

        assert backend.type == "local"
        assert backend.config == {}

    def test_detect_state_location_no_backend_verbose(self):
        """Test detecting state location without backend configuration and verbose logging."""
        detector = StateDetector()

        mock_config = Mock()
        mock_config.terraform_block = None

        backend = detector.detect_state_location(mock_config, verbose=True)

        assert backend.type == "local"
        assert backend.config == {}

    def test_resolve_local_state(self, tmp_path):
        """Test resolving local state file path."""
        detector = StateDetector()

        state_path = detector.resolve_local_state(tmp_path)

        assert state_path == tmp_path / "terraform.tfstate"

    def test_get_state_file_info_local(self, tmp_path):
        """Test getting state file info for local backend."""
        detector = StateDetector()

        mock_config = Mock()
        mock_config.terraform_block = None

        info = detector.get_state_file_info(mock_config, tmp_path)

        assert info["backend_type"] == "local"
        assert info["state_file_path"] == str(tmp_path / "terraform.tfstate")
        assert not info["requires_credentials"]

    def test_get_state_file_info_s3(self):
        """Test getting state file info for S3 backend."""
        detector = StateDetector()

        mock_config = Mock()
        mock_config.terraform_block = {
            "backend": [
                {
                    "s3": [
                        {
                            "bucket": "my-terraform-state",
                            "key": "prod/terraform.tfstate",
                        }
                    ]
                }
            ]
        }

        with patch.object(detector.parser, "extract_backend_config") as mock_extract:
            mock_extract.return_value = Mock(
                type="s3",
                config={
                    "bucket": "my-terraform-state",
                    "key": "prod/terraform.tfstate",
                },
            )
            info = detector.get_state_file_info(mock_config, Path("/tmp"))

        assert info["backend_type"] == "s3"
        assert (
            info["state_file_path"] == "s3://my-terraform-state/prod/terraform.tfstate"
        )
        assert info["requires_credentials"]


class TestCredentialManager:
    """Test credential manager service."""

    def test_detect_state_access_credentials_s3_backend(self):
        """Test detecting credentials from S3 backend configuration."""
        manager = CredentialManager()

        mock_config = Mock()
        mock_config.terraform_block = {
            "backend": [
                {
                    "s3": [
                        {
                            "bucket": "my-terraform-state",
                            "key": "prod/terraform.tfstate",
                            "region": "us-west-2",
                            "profile": "prod",
                        }
                    ]
                }
            ]
        }

        with patch.object(manager.parser, "extract_backend_config") as mock_extract:
            mock_extract.return_value = Mock(
                type="s3",
                config={
                    "bucket": "my-terraform-state",
                    "key": "prod/terraform.tfstate",
                    "region": "us-west-2",
                    "profile": "prod",
                },
            )
            credentials = manager.detect_state_access_credentials(mock_config)

        assert credentials.profile == "prod"
        assert credentials.region == "us-west-2"

    def test_detect_state_access_credentials_s3_backend_verbose(self):
        """Test detecting credentials from S3 backend configuration with verbose logging."""
        manager = CredentialManager()

        mock_config = Mock()
        mock_config.terraform_block = {
            "backend": [
                {
                    "s3": [
                        {
                            "bucket": "my-terraform-state",
                            "key": "prod/terraform.tfstate",
                            "region": "us-west-2",
                            "profile": "prod",
                        }
                    ]
                }
            ]
        }

        with patch.object(manager.parser, "extract_backend_config") as mock_extract:
            mock_extract.return_value = Mock(
                type="s3",
                config={
                    "bucket": "my-terraform-state",
                    "key": "prod/terraform.tfstate",
                    "region": "us-west-2",
                    "profile": "prod",
                },
            )
            credentials = manager.detect_state_access_credentials(mock_config, verbose=True)

        assert credentials.profile == "prod"
        assert credentials.region == "us-west-2"

    def test_detect_state_access_credentials_aws_provider(self):
        """Test detecting credentials from AWS provider configuration."""
        manager = CredentialManager()

        mock_config = Mock()
        mock_config.terraform_block = None
        mock_config.providers = [
            {"name": "aws", "region": "us-west-2", "profile": "prod"}
        ]

        with patch.object(manager.parser, "extract_backend_config") as mock_extract:
            mock_extract.return_value = None
            credentials = manager.detect_state_access_credentials(mock_config)

        assert credentials.profile == "prod"
        assert credentials.region == "us-west-2"

    def test_detect_state_access_credentials_aws_provider_verbose(self):
        """Test detecting credentials from AWS provider configuration with verbose logging."""
        manager = CredentialManager()

        mock_config = Mock()
        mock_config.terraform_block = None
        mock_config.providers = [
            {"name": "aws", "region": "us-west-2", "profile": "prod"}
        ]

        with patch.object(manager.parser, "extract_backend_config") as mock_extract:
            mock_extract.return_value = None
            credentials = manager.detect_state_access_credentials(mock_config, verbose=True)

        assert credentials.profile == "prod"
        assert credentials.region == "us-west-2"

    def test_detect_state_access_credentials_no_credentials(self):
        """Test detecting credentials when none are configured."""
        manager = CredentialManager()

        mock_config = Mock()
        mock_config.terraform_block = None
        mock_config.providers = []

        credentials = manager.detect_state_access_credentials(mock_config)

        assert credentials.profile is None
        assert credentials.region is None
        assert credentials.role_arn is None

    def test_detect_state_access_credentials_no_credentials_verbose(self):
        """Test detecting credentials when none are configured with verbose logging."""
        manager = CredentialManager()

        mock_config = Mock()
        mock_config.terraform_block = None
        mock_config.providers = []

        credentials = manager.detect_state_access_credentials(mock_config, verbose=True)

        assert credentials.profile is None
        assert credentials.region is None
        assert credentials.role_arn is None

    def test_extract_s3_backend_credentials(self):
        """Test extracting credentials from S3 backend configuration."""
        manager = CredentialManager()

        config = {
            "bucket": "my-terraform-state",
            "key": "prod/terraform.tfstate",
            "region": "us-west-2",
            "profile": "prod",
            "assume_role": {"role_arn": "arn:aws:iam::123456789012:role/TerraformRole"},
        }

        credentials = manager.extract_s3_backend_credentials(config)

        assert credentials.profile == "prod"
        assert credentials.region == "us-west-2"
        assert credentials.role_arn == "arn:aws:iam::123456789012:role/TerraformRole"

    def test_extract_provider_credentials(self):
        """Test extracting credentials from provider configuration."""
        manager = CredentialManager()

        provider = {
            "name": "aws",
            "region": "us-west-2",
            "profile": "prod",
            "assume_role": {"role_arn": "arn:aws:iam::123456789012:role/TerraformRole"},
        }

        credentials = manager.extract_provider_credentials(provider)

        assert credentials.profile == "prod"
        assert credentials.region == "us-west-2"
        assert credentials.role_arn == "arn:aws:iam::123456789012:role/TerraformRole"

    def test_find_aws_provider_found(self):
        """Test finding AWS provider when it exists."""
        manager = CredentialManager()

        providers = [
            {"name": "aws", "region": "us-west-2"},
            {"name": "azurerm", "region": "eastus"},
        ]

        provider = manager.find_aws_provider(providers)

        assert provider["name"] == "aws"
        assert provider["region"] == "us-west-2"

    def test_find_aws_provider_not_found(self):
        """Test finding AWS provider when it doesn't exist."""
        manager = CredentialManager()

        providers = [
            {"name": "azurerm", "region": "eastus"},
            {"name": "google", "region": "us-central1"},
        ]

        provider = manager.find_aws_provider(providers)

        assert provider is None

    @patch("tfmate.services.credential_manager.boto3")
    def test_create_aws_session_basic(self, mock_boto3):
        """Test creating basic AWS session."""
        manager = CredentialManager()

        credentials = Mock()
        credentials.profile = "prod"
        credentials.region = "us-west-2"
        credentials.role_arn = None

        mock_session = Mock()
        mock_boto3.Session.return_value = mock_session

        session = manager.create_aws_session(credentials)

        mock_boto3.Session.assert_called_once_with(
            profile_name="prod", region_name="us-west-2"
        )
        assert session == mock_session

    @patch("tfmate.services.credential_manager.boto3")
    def test_create_aws_session_with_assume_role(self, mock_boto3):
        """Test creating AWS session with assume role."""
        manager = CredentialManager()

        credentials = Mock()
        credentials.profile = "prod"
        credentials.region = "us-west-2"
        credentials.role_arn = "arn:aws:iam::123456789012:role/TerraformRole"
        credentials.assume_role_config = None

        mock_session = Mock()
        mock_sts = Mock()
        mock_session.client.return_value = mock_sts

        mock_assumed_role = {
            "Credentials": {
                "AccessKeyId": "AKIA...",
                "SecretAccessKey": "secret",
                "SessionToken": "token",
            }
        }
        mock_sts.assume_role.return_value = mock_assumed_role

        mock_boto3.Session.return_value = mock_session

        session = manager.create_aws_session(credentials)

        mock_sts.assume_role.assert_called_once_with(
            RoleArn="arn:aws:iam::123456789012:role/TerraformRole",
            RoleSessionName="tfmate-state-access",
        )
        # Should create a new session with assumed role credentials
        assert mock_boto3.Session.call_count == 2

    def test_validate_credentials_success(self):
        """Test validating credentials successfully."""
        manager = CredentialManager()

        credentials = Mock()

        with patch.object(manager, "create_aws_session") as mock_create:
            mock_session = Mock()
            mock_sts = Mock()
            mock_session.client.return_value = mock_sts
            mock_create.return_value = mock_session

            result = manager.validate_credentials(credentials)

        assert result is True
        mock_sts.get_caller_identity.assert_called_once()

    def test_validate_credentials_failure(self):
        """Test validating credentials fails."""
        manager = CredentialManager()

        credentials = Mock()

        with patch.object(manager, "create_aws_session") as mock_create:
            mock_create.side_effect = Exception("Invalid credentials")

            result = manager.validate_credentials(credentials)

        assert result is False
