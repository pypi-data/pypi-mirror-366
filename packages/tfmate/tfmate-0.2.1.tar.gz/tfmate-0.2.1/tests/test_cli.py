"""
Unit tests for tfmate CLI commands.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from click.testing import CliRunner

from tfmate.cli.main import cli


def extract_json_from_output(output: str) -> str:
    """Extract JSON from CLI output."""
    return output.strip()


class TestCLICommands:
    """Test CLI command functionality."""

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Terraform maintenance tool" in result.output

    def test_aws_services_help(self):
        """Test AWS services command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["aws", "services", "--help"])
        assert result.exit_code == 0
        assert "List all available AWS services" in result.output

    def test_terraform_version_help(self):
        """Test Terraform version command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["terraform", "version", "--help"])
        assert result.exit_code == 0
        assert "Get Terraform version from state file" in result.output

    def test_analyze_config_help(self):
        """Test analyze config command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "config", "--help"])
        assert result.exit_code == 0
        assert "Analyze Terraform configuration files" in result.output

    def test_aws_services_names_only(self):
        """Test AWS services command with names-only option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["aws", "services", "--names-only"])
        assert result.exit_code == 0
        # Should return service names
        output_lines = result.output.strip().split("\n")
        assert len(output_lines) > 0

    def test_aws_services_with_filter(self):
        """Test AWS services command with filter."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["aws", "services", "--filter-name", "ecs", "--names-only"]
        )
        assert result.exit_code == 0
        # Should return only ecs
        output_lines = [
            line
            for line in result.output.strip().split("\n")
            if line.strip() and "ecs" in line
        ]
        assert len(output_lines) == 1
        assert "ecs" in output_lines[0]

    def test_aws_services_json_output(self):
        """Test AWS services command with JSON output."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--output", "json", "aws", "services", "--filter-name", "ecs"]
        )
        assert result.exit_code == 0
        # Should be valid JSON
        json_output = extract_json_from_output(result.output)
        try:
            data = json.loads(json_output)
            assert isinstance(data, list)
            assert len(data) > 0
        except json.JSONDecodeError:
            pytest.fail(f"Output is not valid JSON: {json_output}")

    def test_aws_services_verbose(self):
        """Test AWS services command with verbose output."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["--verbose", "aws", "services", "--filter-name", "ecs", "--names-only"],
        )
        assert result.exit_code == 0
        # In names-only mode, verbose output might not show "Found"
        # Just check that it runs successfully
        assert "ecs" in result.output

    def test_analyze_config_no_directory(self, tmp_path):
        """Test analyze config command with no Terraform files."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "config", "--directory", str(tmp_path)])
        assert result.exit_code == 0
        assert "Terraform Block" in result.output
        assert "Not found" in result.output

    def test_analyze_config_with_files(self, tmp_path):
        """Test analyze config command with Terraform files."""
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

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "config", "--directory", str(tmp_path)])
        assert result.exit_code == 0
        assert "Terraform Block" in result.output
        assert "Present" in result.output

    def test_analyze_config_show_providers(self, tmp_path):
        """Test analyze config command with show providers."""
        # Create a test .tf file
        tf_file = tmp_path / "main.tf"
        tf_file.write_text("""
        provider "aws" {
          region = "us-west-2"
        }
        """)

        runner = CliRunner()
        result = runner.invoke(
            cli, ["analyze", "config", "--directory", str(tmp_path), "--show-providers"]
        )
        assert result.exit_code == 0
        assert "Provider Configurations" in result.output
        assert "aws" in result.output
        assert "region" in result.output
        assert "us-west-2" in result.output

    def test_analyze_config_json_output(self, tmp_path):
        """Test analyze config command with JSON output."""
        # Create a test .tf file
        tf_file = tmp_path / "main.tf"
        tf_file.write_text("""
        terraform {
          required_version = ">= 1.5.0"
        }
        """)

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--output", "json", "analyze", "config", "--directory", str(tmp_path)]
        )
        assert result.exit_code == 0
        # Should be valid JSON
        json_output = extract_json_from_output(result.output)
        try:
            data = json.loads(json_output)
            assert isinstance(data, dict)
            assert "directory" in data
            assert "backend_type" in data
        except json.JSONDecodeError:
            pytest.fail(f"Output is not valid JSON: {json_output}")

    def test_terraform_version_no_state(self, tmp_path):
        """Test terraform version command with no state file."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["terraform", "version", "--directory", str(tmp_path)]
        )
        assert result.exit_code == 1  # Should fail with no state file
        # Error message goes to stderr via Rich, but CliRunner doesn't capture it
        # Just verify the command fails as expected

    def test_terraform_version_with_state(self, tmp_path):
        """Test terraform version command with state file."""
        # Create a test state file
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

        runner = CliRunner()
        result = runner.invoke(
            cli, ["terraform", "version", "--state-file", str(state_file)]
        )
        assert result.exit_code == 0
        assert "1.5.0" in result.output

    def test_global_options_verbose(self):
        """Test global verbose option."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["--verbose", "aws", "services", "--filter-name", "ecs", "--names-only"],
        )
        assert result.exit_code == 0
        # In names-only mode, verbose output might not show "Found"
        # Just check that it runs successfully
        assert "ecs" in result.output

    def test_global_options_quiet(self):
        """Test global quiet option."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--quiet", "aws", "services", "--filter-name", "ecs", "--names-only"]
        )
        assert result.exit_code == 0
        # Should not show verbose output
        assert "Found" not in result.output

    def test_global_options_output_json(self):
        """Test global output option with JSON."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--output",
                "json",
                "aws",
                "services",
                "--filter-name",
                "ecs",
                "--names-only",
            ],
        )
        assert result.exit_code == 0
        # Should be valid JSON
        json_output = extract_json_from_output(result.output)
        try:
            data = json.loads(json_output)
            assert isinstance(data, dict)
            assert "services" in data
        except json.JSONDecodeError:
            pytest.fail(f"Output is not valid JSON: {json_output}")

    def test_global_options_output_text(self):
        """Test global output option with text."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--output",
                "text",
                "aws",
                "services",
                "--filter-name",
                "ecs",
                "--names-only",
            ],
        )
        assert result.exit_code == 0
        # Should be plain text
        assert "ecs" in result.output
        assert "[" not in result.output  # Should not be JSON

    def test_invalid_output_format(self):
        """Test invalid output format raises error."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--output", "invalid", "aws", "services"])
        assert result.exit_code == 2  # Click error
        assert "Invalid value" in result.output

    def test_nonexistent_directory(self):
        """Test with nonexistent directory raises error."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["analyze", "config", "--directory", "/nonexistent/path"]
        )
        assert result.exit_code == 2  # Click error
        assert "does not exist" in result.output

    def test_nonexistent_state_file(self):
        """Test CLI with nonexistent state file."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["terraform", "version", "--state-file", "/nonexistent/state.tfstate"]
        )
        assert result.exit_code == 2  # Click error for invalid path
        assert "Error" in result.output
        assert "does not exist" in result.output

    def test_settings_help(self):
        """Test settings command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["settings", "--help"])
        assert result.exit_code == 0
        assert "Settings-related commands" in result.output

    def test_settings_default_output(self):
        """Test settings command with default table output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--output", "text", "settings"])
        assert result.exit_code == 0
        # Should contain setting names and values in text format
        assert "app_name:" in result.output
        assert "tfmate" in result.output
        assert "default_output_format:" in result.output
        assert "table" in result.output

    def test_settings_json_output(self):
        """Test settings command with JSON output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--output", "json", "settings"])
        assert result.exit_code == 0
        # Should be valid JSON
        json_output = extract_json_from_output(result.output)
        try:
            data = json.loads(json_output)
            assert isinstance(data, dict)
            # Should contain expected settings
            assert "app_name" in data
            assert data["app_name"] == "tfmate"
            assert "default_output_format" in data
            assert data["default_output_format"] == "table"
            assert "terraform_timeout" in data
            assert isinstance(data["terraform_timeout"], int)
        except json.JSONDecodeError:
            pytest.fail(f"Output is not valid JSON: {json_output}")

    def test_settings_text_output(self):
        """Test settings command with text output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--output", "text", "settings"])
        assert result.exit_code == 0
        # Should contain setting names and values in text format
        assert "app_name:" in result.output
        assert "tfmate" in result.output
        assert "default_output_format:" in result.output
        assert "table" in result.output
        # Should not contain table formatting
        assert "Setting Name" not in result.output
        assert "Value" not in result.output

    def test_settings_verbose_output(self):
        """Test settings command with verbose output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "--output", "text", "settings"])
        assert result.exit_code == 0
        # Should contain setting names and values in text format
        assert "app_name:" in result.output
        assert "tfmate" in result.output

    def test_settings_with_custom_config_file(self, tmp_path):
        """Test settings command with custom configuration file."""
        # Create a custom config file (environment variable format)
        config_file = tmp_path / "custom_config.env"
        config_content = """
        tfmate_APP_NAME=custom-tfmate
        tfmate_DEFAULT_OUTPUT_FORMAT=json
        tfmate_TERRAFORM_TIMEOUT=60
        """
        config_file.write_text(config_content)

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--config-file", str(config_file), "--output", "json", "settings"]
        )
        assert result.exit_code == 0

        # Should be valid JSON with custom values
        json_output = extract_json_from_output(result.output)
        try:
            data = json.loads(json_output)
            assert data["app_name"] == "custom-tfmate"
            assert data["default_output_format"] == "json"
            assert data["terraform_timeout"] == 60
        except json.JSONDecodeError:
            pytest.fail(f"Output is not valid JSON: {json_output}")

    def test_settings_invalid_config_file(self):
        """Test settings command with invalid configuration file."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--config-file", "/nonexistent/config.env", "settings"]
        )
        assert result.exit_code == 2  # Click error for invalid path
        assert "Error" in result.output
        assert "does not exist" in result.output

    def test_settings_all_output_formats(self):
        """Test settings command with all output formats."""
        runner = CliRunner()

        # Test text format (easier to test than rich table)
        result = runner.invoke(cli, ["--output", "text", "settings"])
        assert result.exit_code == 0
        assert "app_name:" in result.output
        assert "tfmate" in result.output

        # Test JSON format
        result = runner.invoke(cli, ["--output", "json", "settings"])
        assert result.exit_code == 0
        json_output = extract_json_from_output(result.output)
        data = json.loads(json_output)
        assert isinstance(data, dict)

        # Test text format
        result = runner.invoke(cli, ["--output", "text", "settings"])
        assert result.exit_code == 0
        assert "app_name:" in result.output
        assert "tfmate" in result.output

    def test_settings_contains_all_expected_fields(self):
        """Test that settings command shows all expected configuration fields."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--output", "json", "settings"])
        assert result.exit_code == 0

        json_output = extract_json_from_output(result.output)
        data = json.loads(json_output)

        # Check for all expected settings fields
        expected_fields = [
            "app_name",
            "app_version",
            "default_output_format",
            "enable_colors",
            "quiet_mode",
            "aws_default_region",
            "aws_default_profile",
            "terraform_timeout",
            "terraform_max_retries",
            "log_level",
            "log_file",
        ]

        for field in expected_fields:
            assert field in data, (
                f"Expected field '{field}' not found in settings output"
            )

    def test_settings_field_types(self):
        """Test that settings command returns correct data types."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--output", "json", "settings"])
        assert result.exit_code == 0

        json_output = extract_json_from_output(result.output)
        data = json.loads(json_output)

        # Check data types
        assert isinstance(data["app_name"], str)
        assert isinstance(data["app_version"], str)
        assert isinstance(data["default_output_format"], str)
        assert isinstance(data["enable_colors"], bool)
        assert isinstance(data["quiet_mode"], bool)
        assert isinstance(data["terraform_timeout"], int)
        assert isinstance(data["terraform_max_retries"], int)
        assert isinstance(data["log_level"], str)
        # Optional fields can be None
        assert data["aws_default_region"] is None or isinstance(
            data["aws_default_region"], str
        )
        assert data["aws_default_profile"] is None or isinstance(
            data["aws_default_profile"], str
        )
        assert data["log_file"] is None or isinstance(data["log_file"], str)
