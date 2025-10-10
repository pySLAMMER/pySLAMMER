"""
Verification framework for pySLAMMER against legacy SLAMMER results.

This package provides tools for automated verification of pySLAMMER results
against legacy SLAMMER results using a robust, cached testing framework.
"""

from .data_loader import DataManager, ConfigManager
from .schemas import ValidationError

__version__ = "1.0.0"
__all__ = ["DataManager", "ConfigManager", "ValidationError"]