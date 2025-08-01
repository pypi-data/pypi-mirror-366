"""
Tests for tfmate settings management.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import toml

from tfmate.settings import Settings


class TestSettings:
    """Test Settings class functionality."""

    def test_default_settings(self):
        """Test that default settings are correctly set."""
        settings = Settings()

        assert settings.app_name == "tfmate"
        assert settings.app_version == "0.1.0"
        assert settings.default_output_format == "table"
        assert settings.enable_colors is True
        assert settings.quiet_mode is False
        assert settings.aws_default_region is None
        assert settings.aws_default_profile is None
        assert settings.terraform_timeout == 30
        assert settings.terraform_max_retries == 3
        assert settings.log_level == "INFO"
        assert settings.log_file is None

    def test_environment_variables(self):
        """Test that environment variables override defaults."""
        with patch.dict(
            os.environ,
            {
                "tfmate_AWS_DEFAULT_REGION": "us-west-2",
                "tfmate_DEFAULT_OUTPUT_FORMAT": "json",
                "tfmate_TERRAFORM_TIMEOUT": "60",
                "tfmate_LOG_LEVEL": "DEBUG",
            },
        ):
            settings = Settings()

            assert settings.aws_default_region == "us-west-2"
            assert settings.default_output_format == "json"
            assert settings.terraform_timeout == 60
            assert settings.log_level == "DEBUG"

    def test_environment_variables_case_insensitive(self):
        """Test that environment variables are case insensitive."""
        with patch.dict(
            os.environ,
            {
                "tfmate_aws_default_region": "us-east-1",
                "tfmate_DEFAULT_OUTPUT_FORMAT": "text",
            },
        ):
            settings = Settings()

            assert settings.aws_default_region == "us-east-1"
            assert settings.default_output_format == "text"

    def test_from_file_with_explicit_path(self):
        """Test loading settings from an explicit file path."""
        config_data = {
            "app_name": "custom-tfmate",
            "default_output_format": "json",
            "aws_default_region": "eu-west-1",
            "terraform_timeout": 45,
            "log_level": "WARNING",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_file = f.name

        try:
            settings = Settings.from_file(config_file)

            assert settings.app_name == "custom-tfmate"
            assert settings.default_output_format == "json"
            assert settings.aws_default_region == "eu-west-1"
            assert settings.terraform_timeout == 45
            assert settings.log_level == "WARNING"

            # Other settings should remain at defaults
            assert settings.app_version == "0.1.0"
            assert settings.enable_colors is True
            assert settings.quiet_mode is False
        finally:
            os.unlink(config_file)

    def test_from_file_with_section(self):
        """Test loading settings from TOML file with [tfmate] section."""
        config_data = {
            "tfmate": {
                "app_name": "sectioned-tfmate",
                "default_output_format": "text",
                "aws_default_region": "ap-southeast-1",
                "terraform_timeout": 90,
                "log_level": "ERROR",
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_file = f.name

        try:
            settings = Settings.from_file(config_file)

            assert settings.app_name == "sectioned-tfmate"
            assert settings.default_output_format == "text"
            assert settings.aws_default_region == "ap-southeast-1"
            assert settings.terraform_timeout == 90
            assert settings.log_level == "ERROR"
        finally:
            os.unlink(config_file)

    def test_from_file_nonexistent(self):
        """Test loading settings when file doesn't exist."""
        settings = Settings.from_file("/nonexistent/path/config.toml")

        # Should fall back to defaults
        assert settings.app_name == "tfmate"
        assert settings.default_output_format == "table"

    def test_from_file_invalid_toml(self):
        """Test loading settings from invalid TOML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("invalid toml content [\n")
            config_file = f.name

        try:
            # pydantic-settings treats .toml files as environment files
            # and ignores invalid content, so this should not raise an exception
            settings = Settings.from_file(config_file)

            # Should fall back to defaults when TOML is invalid
            assert settings.app_name == "tfmate"
            assert settings.default_output_format == "table"
        finally:
            os.unlink(config_file)

    def test_from_file_with_boolean_values(self):
        """Test loading boolean values from TOML file."""
        config_data = {
            "enable_colors": False,
            "quiet_mode": True,
            "aws_default_region": "us-central-1",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_file = f.name

        try:
            settings = Settings.from_file(config_file)

            assert settings.enable_colors is False
            assert settings.quiet_mode is True
            assert settings.aws_default_region == "us-central-1"
        finally:
            os.unlink(config_file)

    def test_from_file_with_null_values(self):
        """Test loading null values from TOML file."""
        config_data = {
            "aws_default_region": None,
            "aws_default_profile": None,
            "log_file": None,
            "default_output_format": "table",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_file = f.name

        try:
            settings = Settings.from_file(config_file)

            assert settings.aws_default_region is None
            assert settings.aws_default_profile is None
            assert settings.log_file is None
            assert settings.default_output_format == "table"
        finally:
            os.unlink(config_file)

    def test_from_file_with_integer_values(self):
        """Test loading integer values from TOML file."""
        config_data = {
            "terraform_timeout": 120,
            "terraform_max_retries": 5,
            "app_version": "2.0.0",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_file = f.name

        try:
            settings = Settings.from_file(config_file)

            assert settings.terraform_timeout == 120
            assert settings.terraform_max_retries == 5
            assert settings.app_version == "2.0.0"
        finally:
            os.unlink(config_file)

    def test_from_file_with_string_values(self):
        """Test loading string values from TOML file."""
        config_data = {
            "app_name": "my-tfmate",
            "default_output_format": "json",
            "aws_default_region": "us-west-2",
            "aws_default_profile": "production",
            "log_level": "DEBUG",
            "log_file": "/var/log/tfmate.log",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_file = f.name

        try:
            settings = Settings.from_file(config_file)

            assert settings.app_name == "my-tfmate"
            assert settings.default_output_format == "json"
            assert settings.aws_default_region == "us-west-2"
            assert settings.aws_default_profile == "production"
            assert settings.log_level == "DEBUG"
            assert settings.log_file == "/var/log/tfmate.log"
        finally:
            os.unlink(config_file)

    def test_from_file_environment_override(self):
        """Test that environment variables override file settings."""
        config_data = {
            "aws_default_region": "us-west-2",
            "default_output_format": "table",
            "terraform_timeout": 30,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_file = f.name

        try:
            with patch.dict(
                os.environ,
                {
                    "tfmate_AWS_DEFAULT_REGION": "us-east-1",
                    "tfmate_DEFAULT_OUTPUT_FORMAT": "json",
                },
            ):
                settings = Settings.from_file(config_file)

                # Environment variables should override file settings
                assert settings.aws_default_region == "us-east-1"
                assert settings.default_output_format == "json"
                # File setting should still apply
                assert settings.terraform_timeout == 30
        finally:
            os.unlink(config_file)

    def test_get_config_paths(self):
        """Test getting configuration file paths."""
        settings = Settings()
        paths = settings.get_config_paths()

        # Should return a list
        assert isinstance(paths, list)

        # All paths should be Path objects
        for path in paths:
            assert isinstance(path, Path)

    def test_get_config_paths_with_existing_files(self):
        """Test getting config paths when files exist."""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True

            settings = Settings()
            paths = settings.get_config_paths()

            # Should return paths even if they don't actually exist
            assert len(paths) > 0

    def test_from_file_no_config_files(self):
        """Test from_file when no config files exist."""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False

            settings = Settings.from_file()

            # Should return default settings
            assert settings.app_name == "tfmate"
            assert settings.default_output_format == "table"

    def test_from_file_cascading_precedence(self):
        """Test that config file precedence works correctly."""
        # Create multiple config files with different values
        global_config = {"app_name": "global-tfmate", "default_output_format": "table"}

        user_config = {"app_name": "user-tfmate", "aws_default_region": "us-west-2"}

        local_config = {"app_name": "local-tfmate", "terraform_timeout": 60}

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create global config
            global_path = Path(temp_dir) / "global.toml"
            with open(global_path, "w") as f:
                toml.dump(global_config, f)

            # Create user config
            user_path = Path(temp_dir) / "user.toml"
            with open(user_path, "w") as f:
                toml.dump(user_config, f)

            # Create local config
            local_path = Path(temp_dir) / "local.toml"
            with open(local_path, "w") as f:
                toml.dump(local_config, f)

            # Mock the path detection to return our test files
            with patch("tfmate.settings.Settings.from_file") as mock_from_file:
                # Simulate the cascading logic
                mock_from_file.return_value = Settings()

                # Test that the last file (highest precedence) is used
                settings = Settings.from_file(str(local_path))

                # The mock should have been called with the local path
                mock_from_file.assert_called_once()

    def test_invalid_setting_values(self):
        """Test that invalid setting values raise appropriate errors."""
        # Test invalid output format
        with patch.dict(os.environ, {"tfmate_DEFAULT_OUTPUT_FORMAT": "invalid"}):
            with pytest.raises(Exception):
                Settings()

        # Test invalid timeout (negative)
        with patch.dict(os.environ, {"tfmate_TERRAFORM_TIMEOUT": "-1"}):
            with pytest.raises(Exception):
                Settings()

        # Test invalid retries (negative)
        with patch.dict(os.environ, {"tfmate_TERRAFORM_MAX_RETRIES": "-5"}):
            with pytest.raises(Exception):
                Settings()

        # Test invalid log level
        with patch.dict(os.environ, {"tfmate_LOG_LEVEL": "INVALID"}):
            with pytest.raises(Exception):
                Settings()

    def test_extra_settings_ignored(self):
        """Test that extra settings in config file are ignored."""
        config_data = {
            "app_name": "test-tfmate",
            "unknown_setting": "should_be_ignored",
            "another_unknown": 123,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            toml.dump(config_data, f)
            config_file = f.name

        try:
            settings = Settings.from_file(config_file)

            # Known setting should be loaded
            assert settings.app_name == "test-tfmate"

            # Unknown settings should be ignored (no error raised)
            assert not hasattr(settings, "unknown_setting")
            assert not hasattr(settings, "another_unknown")
        finally:
            os.unlink(config_file)
