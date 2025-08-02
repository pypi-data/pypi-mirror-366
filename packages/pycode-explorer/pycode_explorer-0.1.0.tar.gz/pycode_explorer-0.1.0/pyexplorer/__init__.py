"""
PyExplorer - A Python package for analyzing scripts and exploring package functionalities

This package provides tools to:
1. Analyze Python scripts to understand their imports and function usage
2. Explore installed packages and their available functions
"""

from .script_analyzer import ScriptAnalyzer
from .package_explorer import PackageExplorer

__version__ = "0.1.0"
__author__ = "Your Name"

# Make the main classes available at package level
__all__ = ["ScriptAnalyzer", "PackageExplorer"]