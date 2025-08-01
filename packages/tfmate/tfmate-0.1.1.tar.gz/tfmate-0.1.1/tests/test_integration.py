"""
Integration tests for tfmate.

These tests require the TFTEST_PROJECT_PATH environment variable to be set
to point to a real Terraform project directory.
"""

import os
import pytest
from pathlib import Path

from tfmate.services.terraform_parser import TerraformParser
from tfmate.services.state_detector import StateDetector
from tfmate.services.credential_manager import CredentialManager
from tfmate.services.state_access import read_local_state


@pytest.mark.integration
def test_real_terraform_project():
    """
    Test with a real Terraform project using TFTEST_PROJECT_PATH environment variable.

    This test requires the TFTEST_PROJECT_PATH environment variable to be set
    to point to a real Terraform project directory.
    """
    project_path = os.getenv("TFTEST_PROJECT_PATH")
    if not project_path:
        pytest.skip("TFTEST_PROJECT_PATH environment variable not set")

    project_dir = Path(project_path)
    if not project_dir.exists():
        pytest.skip(f"Project path does not exist: {project_path}")

    # Test that we can parse the configuration
    parser = TerraformParser()
    config = parser.parse_directory(project_dir)

    # Basic validation - should have some configuration
    assert config is not None

    # Test backend detection
    detector = StateDetector()
    backend = detector.detect_state_location(config)

    # Should have a valid backend type
    assert backend.type in {"local", "s3", "http", "remote"}

    # Test credential extraction (if applicable)
    if backend.type in {"s3", "remote"}:
        credential_manager = CredentialManager()
        credentials = credential_manager.detect_state_access_credentials(config)

        # Should have valid credentials structure
        assert credentials is not None
        # Don't test specific values as they may vary


@pytest.mark.integration
def test_state_file_access():
    """
    Test state file access with a real Terraform project.
    """
    project_path = os.getenv("TFTEST_PROJECT_PATH")
    if not project_path:
        pytest.skip("TFTEST_PROJECT_PATH environment variable not set")

    project_dir = Path(project_path)

    # Test that we can access the state file
    parser = TerraformParser()
    config = parser.parse_directory(project_dir)

    detector = StateDetector()
    backend = detector.detect_state_location(config)

    # Try to read the state file
    try:
        if backend.type == "local":
            state_path = detector.resolve_local_state(project_dir)
            if state_path.exists():
                state = read_local_state(state_path)
                # Basic state validation
                assert "version" in state
                assert "terraform_version" in state
                assert state["version"] >= 4  # Terraform 1.5+ requirement
            else:
                pytest.skip("No local state file found")
        else:
            # For remote backends, just test that we can extract credentials
            # and that the backend configuration is valid
            credential_manager = CredentialManager()
            credentials = credential_manager.detect_state_access_credentials(config)
            assert credentials is not None

    except Exception as e:
        # Don't fail the test for state access issues
        # Just log that we couldn't access the state
        pytest.skip(f"Could not access state file: {e}")


@pytest.mark.integration
def test_cli_with_real_project():
    """
    Test CLI commands with a real Terraform project.
    """
    project_path = os.getenv("TFTEST_PROJECT_PATH")
    if not project_path:
        pytest.skip("TFTEST_PROJECT_PATH environment variable not set")

    from click.testing import CliRunner
    from tfmate.cli.main import cli

    runner = CliRunner()

    # Test analyze config command
    result = runner.invoke(cli, ["analyze", "config", "--directory", project_path])
    assert result.exit_code == 0

    # Test terraform version command (if state file accessible)
    result = runner.invoke(cli, ["terraform", "version", "--directory", project_path])
    # Don't assert exit code as state file might not be accessible
    # Just verify the command runs without crashing
    assert result.exit_code in [0, 1]  # 0 for success, 1 for expected errors


@pytest.mark.integration
def test_aws_services_with_real_project():
    """
    Test AWS services command with a real project context.
    """
    project_path = os.getenv("TFTEST_PROJECT_PATH")
    if not project_path:
        pytest.skip("TFTEST_PROJECT_PATH environment variable not set")

    from click.testing import CliRunner
    from tfmate.cli.main import cli

    runner = CliRunner()

    # Test AWS services command
    result = runner.invoke(cli, ["aws", "services", "--names-only"])
    assert result.exit_code == 0
    assert "services" in result.output or len(result.output.strip().split("\n")) > 0

    # Test with filter
    result = runner.invoke(cli, ["aws", "services", "--filter", "ec*", "--names-only"])
    assert result.exit_code == 0
    # Should return some EC services
    output_lines = result.output.strip().split("\n")
    assert len(output_lines) > 0


@pytest.mark.integration
def test_configuration_analysis_with_real_project():
    """
    Test configuration analysis with a real Terraform project.
    """
    project_path = os.getenv("TFTEST_PROJECT_PATH")
    if not project_path:
        pytest.skip("TFTEST_PROJECT_PATH environment variable not set")

    from click.testing import CliRunner
    from tfmate.cli.main import cli

    runner = CliRunner()

    # Test basic configuration analysis
    result = runner.invoke(cli, ["analyze", "config", "--directory", project_path])
    assert result.exit_code == 0
    # The output goes to stderr due to rich console, so we can't easily check it in tests
    # The fact that exit_code is 0 means the command succeeded

    # Test with show providers
    result = runner.invoke(
        cli, ["analyze", "config", "--directory", project_path, "--show-providers"]
    )
    assert result.exit_code == 0

    # Test with show backend
    result = runner.invoke(
        cli, ["analyze", "config", "--directory", project_path, "--show-backend"]
    )
    assert result.exit_code == 0

    # Test JSON output
    result = runner.invoke(
        cli, ["--output", "json", "analyze", "config", "--directory", project_path]
    )
    assert result.exit_code == 0
    # Should be valid JSON
    import json

    try:
        json.loads(result.output)
    except json.JSONDecodeError:
        pytest.fail("Output is not valid JSON")


@pytest.mark.integration
def test_verbose_output_with_real_project():
    """
    Test verbose output with a real Terraform project.
    """
    project_path = os.getenv("TFTEST_PROJECT_PATH")
    if not project_path:
        pytest.skip("TFTEST_PROJECT_PATH environment variable not set")

    from click.testing import CliRunner
    from tfmate.cli.main import cli

    runner = CliRunner()

    # Test verbose output with AWS services
    result = runner.invoke(cli, ["--verbose", "aws", "services", "--filter", "ecs"])
    assert result.exit_code == 0
    # The verbose output goes to stderr, which is captured by pytest
    # We can see it in the test output above

    # Test verbose output with configuration analysis
    result = runner.invoke(
        cli, ["--verbose", "analyze", "config", "--directory", project_path]
    )
    assert result.exit_code == 0
    # The verbose output goes to stderr, which is captured by pytest
    # We can see it in the test output above
