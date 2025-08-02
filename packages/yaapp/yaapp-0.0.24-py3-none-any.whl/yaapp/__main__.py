"""
Main entry point for the yaapp CLI command.
Separated to avoid circular imports.
"""

import sys
from yaapp import yaapp as app

def main():
    """Main entry point for the yaapp CLI command."""
    
    # Parse and remove --config option from sys.argv before passing to Click
    config_file = None
    if '--config' in sys.argv:
        try:
            config_index = sys.argv.index('--config')
            if config_index + 1 < len(sys.argv):
                config_file = sys.argv[config_index + 1]
                # Remove --config and its value from sys.argv
                sys.argv.pop(config_index)  # Remove --config
                sys.argv.pop(config_index)  # Remove the config file path
        except (ValueError, IndexError):
            pass
    
    # Also handle -c short form
    if '-c' in sys.argv:
        try:
            config_index = sys.argv.index('-c')
            if config_index + 1 < len(sys.argv):
                config_file = sys.argv[config_index + 1]
                # Remove -c and its value from sys.argv
                sys.argv.pop(config_index)  # Remove -c
                sys.argv.pop(config_index)  # Remove the config file path
        except (ValueError, IndexError):
            pass
    
    # Let the runner system handle everything with optional config
    app.run(config_file=config_file)

if __name__ == "__main__":
    main()