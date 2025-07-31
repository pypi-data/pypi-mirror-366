"""
Pytest configuration for proper import handling.
This eliminates the need for import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src')) in every test file.
"""

import sys
from pathlib import Path
import os

# Add src directory to Python path for tests
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))