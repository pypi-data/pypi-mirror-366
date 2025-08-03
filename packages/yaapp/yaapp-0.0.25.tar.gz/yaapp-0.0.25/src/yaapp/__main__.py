"""
Main entry point for the yaapp CLI command.
Separated to avoid circular imports.
"""

import sys

from yaapp import yaapp


def main():
    yaapp.run()


if __name__ == "__main__":
    main()
