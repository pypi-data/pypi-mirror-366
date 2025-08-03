"""
Main run function for yaapp.

App users should use: from yaapp import run; run()
"""

from .app import Yaapp


def run(config=None):
    """Run yaapp with optional config.

    Args:
        config: Optional config file path

    Returns:
        Result of running the application
    """
    # Import essential runners BEFORE creating app instance
    # This ensures they're available during auto-discovery
    try:
        from .plugins.runners.click.plugin import ClickRunner
    except ImportError:
        pass
    
    # Create fresh instance and run
    app = Yaapp(auto_discover=True, config_file=config)
    return app.run(config)