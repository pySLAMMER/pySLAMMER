"""
Pytest configuration for pySLAMMER verification tests.
"""

import pytest


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--runslow", action="store_true", default=False,
        help="run slow tests"
    )
    parser.addoption(
        "--pyslammer-version",
        action="store", 
        default=None,
        help="Specify pySLAMMER version to test against"
    )


def pytest_configure(config):
    """Configure pytest with custom marks."""
    config.addinivalue_line(
        "markers", "verification: mark test as a verification test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle slow tests."""
    if config.getoption("--runslow"):
        # Run all tests if --runslow is specified
        return
    
    # Skip slow tests by default
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)