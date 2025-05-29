"""
Pytest configuration file.

This file contains fixtures and configuration that will be automatically
available to all test files in the project.
"""

import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root) 