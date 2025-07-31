"""
YApp Client - Creates a YApp that exposes an AppProxy for app-to-app chaining.
"""

import sys
from typing import Optional
from .app import Yaapp
from .plugins import AppProxy


def create_client(target_url: str, name: str = "proxy") -> Yaapp:
    """
    Create a YApp client that proxies to a remote YApp server.
    
    Args:
        target_url: URL of the target YApp server
        name: Name to expose the proxy under (default: "proxy")
        
    Returns:
        YApp instance with AppProxy exposed
    """
    app = Yaapp()
    proxy = AppProxy(target_url)
    app.expose(proxy, name=name, custom=True)
    return app


def main():
    """Main entry point for YApp client."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="YApp Client - Proxy to remote YApp server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m yaapp.client --target http://localhost:8000 tui
  python -m yaapp.client --target http://api.example.com:9000 server --port 8080
  python -m yaapp.client --target http://localhost:8000 --name remote run remote.greet --name Alice
  
Infinite chaining example:
  # Server A on port 8000
  python server_a.py server --port 8000
  
  # Client B proxies to A, exposes on port 8001  
  python -m yaapp.client --target http://localhost:8000 server --port 8001
  
  # Client C proxies to B (which proxies to A), exposes on port 8002
  python -m yaapp.client --target http://localhost:8001 server --port 8002
        """
    )
    
    parser.add_argument(
        "--target", 
        required=True,
        help="Target YApp server URL (e.g., http://localhost:8000)"
    )
    
    parser.add_argument(
        "--name",
        default="proxy", 
        help="Name to expose the proxy under (default: proxy)"
    )
    
    # Parse known args to get client config, then let YApp handle the rest
    args, remaining = parser.parse_known_args()
    
    # Create client app
    app = create_client(args.target, args.name)
    
    # Add remaining args back to sys.argv for YApp to process
    sys.argv = [sys.argv[0]] + remaining
    
    # Run the client app with standard YApp functionality
    app.run()


if __name__ == "__main__":
    main()