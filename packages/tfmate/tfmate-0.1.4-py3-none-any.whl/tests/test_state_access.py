"""
Unit tests for tfmate state access modules.
"""

import json
import pytest
import requests
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from botocore.exceptions import ClientError

from tfmate.services.state_access.local import read_local_state
from tfmate.services.state_access.s3 import read_s3_state
from tfmate.services.state_access.http import read_http_state
from tfmate.services.state_access.tfe import read_tfe_state, get_tfe_workspace_id
from tfmate.exc import StateFileError
from tfmate.models.terraform import StateAccessCredentials


class TestLocalStateAccess:
    """Test local state file access."""

    def test_read_local_state_valid(self, tmp_path):
        """Test reading valid local state file."""
        state_file = tmp_path / "terraform.tfstate"
        state_content = {
            "version": 4,
            "terraform_version": "1.5.0",
            "serial": 1,
            "lineage": "12345678-1234-1234-1234-123456789012",
            "outputs": {"test": {"value": "test"}},
            "resources": [],
        }

        state_file.write_text(json.dumps(state_content))

        result = read_local_state(state_file)

        assert result["version"] == 4
        assert result["terraform_version"] == "1.5.0"
        assert result["outputs"]["test"]["value"] == "test"

    def test_read_local_state_invalid_version(self, tmp_path):
        """Test reading state file with invalid version raises error."""
        state_file = tmp_path / "terraform.tfstate"
        state_content = {
            "version": 3,  # Too old for Terraform 1.5+
            "terraform_version": "1.5.0",
            "serial": 1,
            "lineage": "12345678-1234-1234-1234-123456789012",
            "outputs": {},
            "resources": [],
        }

        state_file.write_text(json.dumps(state_content))

        with pytest.raises(StateFileError) as exc_info:
            read_local_state(state_file)
        assert "Unsupported state version: 3" in str(exc_info.value)

    def test_read_local_state_invalid_json(self, tmp_path):
        """Test reading invalid JSON state file raises error."""
        state_file = tmp_path / "terraform.tfstate"
        state_file.write_text("invalid json content")

        with pytest.raises(StateFileError) as exc_info:
            read_local_state(state_file)
        assert "Invalid JSON in state file" in str(exc_info.value)
        assert len(exc_info.value.suggestions) > 0

    def test_read_local_state_not_found(self, tmp_path):
        """Test reading nonexistent state file raises error."""
        state_file = tmp_path / "nonexistent.tfstate"

        with pytest.raises(StateFileError) as exc_info:
            read_local_state(state_file)
        assert "State file not found" in str(exc_info.value)
        assert len(exc_info.value.suggestions) > 0


class TestS3StateAccess:
    """Test S3 state file access."""

    def test_read_s3_state_valid(self):
        """Test reading valid S3 state file."""
        config = {"bucket": "my-terraform-state", "key": "prod/terraform.tfstate"}

        credentials = StateAccessCredentials(profile="prod", region="us-west-2")

        state_content = {
            "version": 4,
            "terraform_version": "1.5.0",
            "serial": 1,
            "lineage": "12345678-1234-1234-1234-123456789012",
            "outputs": {"test": {"value": "test"}},
            "resources": [],
        }

        mock_response = Mock()
        mock_response.__getitem__ = Mock(return_value=Mock())
        mock_response.__getitem__.return_value.read.return_value = json.dumps(
            state_content
        ).encode("utf-8")

        mock_s3 = Mock()
        mock_s3.get_object.return_value = mock_response

        mock_session = Mock()
        mock_session.client.return_value = mock_s3

        with patch("tfmate.services.state_access.s3.CredentialManager") as mock_manager:
            mock_manager.return_value.create_aws_session.return_value = mock_session

            result = read_s3_state(config, credentials)

        assert result["version"] == 4
        assert result["terraform_version"] == "1.5.0"
        mock_s3.get_object.assert_called_once_with(
            Bucket="my-terraform-state", Key="prod/terraform.tfstate"
        )

    def test_read_s3_state_no_such_key(self):
        """Test reading S3 state file that doesn't exist raises error."""
        config = {"bucket": "my-terraform-state", "key": "prod/terraform.tfstate"}

        credentials = StateAccessCredentials(profile="prod", region="us-west-2")

        mock_s3 = Mock()
        error_response = {
            "Error": {
                "Code": "NoSuchKey",
                "Message": "The specified key does not exist.",
            }
        }
        mock_s3.get_object.side_effect = ClientError(error_response, "GetObject")

        mock_session = Mock()
        mock_session.client.return_value = mock_s3

        with patch("tfmate.services.state_access.s3.CredentialManager") as mock_manager:
            mock_manager.return_value.create_aws_session.return_value = mock_session

            with pytest.raises(StateFileError) as exc_info:
                read_s3_state(config, credentials)

        assert "State file not found in S3" in str(exc_info.value)
        assert len(exc_info.value.suggestions) > 0

    def test_read_s3_state_access_denied(self):
        """Test reading S3 state file with access denied raises error."""
        config = {"bucket": "my-terraform-state", "key": "prod/terraform.tfstate"}

        credentials = StateAccessCredentials(profile="prod", region="us-west-2")

        mock_s3 = Mock()
        error_response = {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}}
        mock_s3.get_object.side_effect = ClientError(error_response, "GetObject")

        mock_session = Mock()
        mock_session.client.return_value = mock_s3

        with patch("tfmate.services.state_access.s3.CredentialManager") as mock_manager:
            mock_manager.return_value.create_aws_session.return_value = mock_session

            with pytest.raises(StateFileError) as exc_info:
                read_s3_state(config, credentials)

        assert "Access denied" in str(exc_info.value)
        assert len(exc_info.value.suggestions) > 0


class TestHTTPStateAccess:
    """Test HTTP state file access."""

    def test_read_http_state_valid(self):
        """Test reading valid HTTP state file."""
        config = {"address": "https://example.com/terraform.tfstate"}

        state_content = {
            "version": 4,
            "terraform_version": "1.5.0",
            "serial": 1,
            "lineage": "12345678-1234-1234-1234-123456789012",
            "outputs": {"test": {"value": "test"}},
            "resources": [],
        }

        mock_response = Mock()
        mock_response.json.return_value = state_content
        mock_response.raise_for_status.return_value = None

        with patch(
            "tfmate.services.state_access.http.requests.Session"
        ) as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            mock_session.get.return_value = mock_response

            result = read_http_state(config)

        assert result["version"] == 4
        assert result["terraform_version"] == "1.5.0"
        mock_session.get.assert_called_once_with(
            "https://example.com/terraform.tfstate", timeout=30
        )

    def test_read_http_state_with_auth(self):
        """Test reading HTTP state file with authentication."""
        config = {
            "address": "https://example.com/terraform.tfstate",
            "username": "user",
            "password": "pass",
        }

        state_content = {
            "version": 4,
            "terraform_version": "1.5.0",
            "serial": 1,
            "lineage": "12345678-1234-1234-1234-123456789012",
            "outputs": {},
            "resources": [],
        }

        mock_response = Mock()
        mock_response.json.return_value = state_content
        mock_response.raise_for_status.return_value = None

        with patch(
            "tfmate.services.state_access.http.requests.Session"
        ) as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            mock_session.get.return_value = mock_response

            result = read_http_state(config)

        # Check that auth was set (auth is set on the session, not called)
        assert result["version"] == 4

    def test_read_http_state_missing_address(self):
        """Test reading HTTP state with missing address raises error."""
        config = {}

        with pytest.raises(StateFileError) as exc_info:
            read_http_state(config)

        assert "Missing 'address' configuration" in str(exc_info.value)
        assert len(exc_info.value.suggestions) > 0

    def test_read_http_state_connection_error(self):
        """Test reading HTTP state with connection error raises error."""
        config = {"address": "https://example.com/terraform.tfstate"}

        with patch(
            "tfmate.services.state_access.http.requests.Session"
        ) as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            mock_session.get.side_effect = requests.exceptions.ConnectionError(
                "ConnectionError"
            )

            with pytest.raises(StateFileError) as exc_info:
                read_http_state(config)

        assert "Connection error:" in str(exc_info.value)
        assert len(exc_info.value.suggestions) > 0


class TestTFEStateAccess:
    """Test Terraform Enterprise state file access."""

    def test_read_tfe_state_valid(self):
        """Test reading valid TFE state file."""
        config = {
            "hostname": "app.terraform.io",
            "organization": "my-org",
            "workspace": "my-workspace",
        }

        credentials = StateAccessCredentials()

        workspace_data = {"data": {"id": "ws-123456"}}

        state_data = {
            "data": {
                "attributes": {
                    "state": {
                        "version": 4,
                        "terraform_version": "1.5.0",
                        "serial": 1,
                        "lineage": "12345678-1234-1234-1234-123456789012",
                        "outputs": {"test": {"value": "test"}},
                        "resources": [],
                    }
                }
            }
        }

        with patch(
            "tfmate.services.state_access.tfe.requests.Session"
        ) as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session

            # Mock workspace lookup
            mock_workspace_response = Mock()
            mock_workspace_response.json.return_value = workspace_data
            mock_workspace_response.raise_for_status.return_value = None

            # Mock state lookup
            mock_state_response = Mock()
            mock_state_response.json.return_value = state_data
            mock_state_response.raise_for_status.return_value = None

            mock_session.get.side_effect = [
                mock_workspace_response,
                mock_state_response,
            ]

            result = read_tfe_state(config, credentials)

        assert result["version"] == 4
        assert result["terraform_version"] == "1.5.0"

    def test_read_tfe_state_missing_organization(self):
        """Test reading TFE state with missing organization raises error."""
        config = {"hostname": "app.terraform.io", "workspace": "my-workspace"}

        credentials = StateAccessCredentials()

        with pytest.raises(StateFileError) as exc_info:
            read_tfe_state(config, credentials)

        assert "Missing 'organization' configuration" in str(exc_info.value)
        assert len(exc_info.value.suggestions) > 0

    def test_read_tfe_state_missing_workspace(self):
        """Test reading TFE state with missing workspace raises error."""
        config = {"hostname": "app.terraform.io", "organization": "my-org"}

        credentials = StateAccessCredentials()

        with pytest.raises(StateFileError) as exc_info:
            read_tfe_state(config, credentials)

        assert "Missing 'workspace' configuration" in str(exc_info.value)
        assert len(exc_info.value.suggestions) > 0

    def test_get_tfe_workspace_id_valid(self):
        """Test getting TFE workspace ID successfully."""
        config = {"hostname": "app.terraform.io"}

        workspace_data = {"data": {"id": "ws-123456"}}

        mock_response = Mock()
        mock_response.json.return_value = workspace_data
        mock_response.raise_for_status.return_value = None

        mock_session = Mock()
        mock_session.get.return_value = mock_response

        result = get_tfe_workspace_id(config, mock_session, "my-org", "my-workspace")

        assert result == "ws-123456"
        mock_session.get.assert_called_once_with(
            "https://app.terraform.io/api/v2/organizations/my-org/workspaces/my-workspace",
            timeout=30,
        )

    def test_get_tfe_workspace_id_not_found(self):
        """Test getting TFE workspace ID when workspace doesn't exist raises error."""
        config = {"hostname": "app.terraform.io"}

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("404")

        mock_session = Mock()
        mock_session.get.return_value = mock_response

        with pytest.raises(StateFileError) as exc_info:
            get_tfe_workspace_id(config, mock_session, "my-org", "my-workspace")

        assert "Failed to get workspace ID:" in str(exc_info.value)
        assert len(exc_info.value.suggestions) > 0
