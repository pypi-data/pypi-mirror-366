"""
Main entry point for the yaapp CLI command.
Separated to avoid circular imports.
"""

import sys

from yaapp import run

if __name__ == "__main__":
    run()
