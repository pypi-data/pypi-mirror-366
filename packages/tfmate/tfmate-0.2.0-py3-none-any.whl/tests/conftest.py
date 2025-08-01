"""
Pytest configuration for tfmate tests.
"""

import os
import pytest


def pytest_configure(config):
    """
    Configure pytest to handle integration test markers.
    """
    config.addinivalue_line("markers", "integration: mark test as integration test")


def pytest_collection_modifyitems(config, items):
    """
    Skip integration tests if TFTEST_PROJECT_PATH is not set.
    """
    skip_integration = pytest.mark.skip(reason="TFTEST_PROJECT_PATH not set")

    for item in items:
        if "integration" in item.keywords:
            if not os.getenv("TFTEST_PROJECT_PATH"):
                item.add_marker(skip_integration)
