#!/usr/bin/env python3
"""
LinkAI-Aion v0.1.6 - Enhanced AI Utilities Library
===================================================

A comprehensive Python utility library by LinkAI for AI projects,
automation, and productivity workflows.

This package provides:
- Text processing and analysis utilities
- File management and organization tools
- Code parsing and language detection
- Real-time file monitoring capabilities
- CLI tools for development workflows

Author: Aksel (CEO, LinkAI)
License: Apache-2.0
Copyright: 2025 LinkAI

For documentation and examples, visit:
https://linkaiapps.com/#linkai-aion
"""

# Define the current version of the package
__version__ = "0.1.6"

# Define the author information
__author__ = "Aksel (CEO, LinkAI)"

# Define the contact email for the package
__email__ = "aksel@linkaiapps.com"

# Define the license type for the package
__license__ = "Apache-2.0"

# Define the copyright information
__copyright__ = "2025 LinkAI"

# Import the text processing module for text analysis and manipulation
from . import text

# Import the file management module for file operations and organization
from . import files

# Import the code parsing module for language detection and code analysis
from . import parser

# Import the file watching module for real-time file monitoring
from . import watcher

# Import the utilities module for general helper functions
from . import utils

# Import the command-line interface module for CLI functionality
from . import cli

# Define the public API exports for the package
__all__ = [
    "__version__",      # Version information
    "__author__",       # Author information
    "__email__",        # Contact email
    "__license__",      # License information
    "__copyright__",    # Copyright information
    "text",             # Text processing module
    "files",            # File management module
    "parser",           # Code parsing module
    "watcher",          # File watching module
    "utils",            # Utilities module
    "cli"               # Command-line interface module
]