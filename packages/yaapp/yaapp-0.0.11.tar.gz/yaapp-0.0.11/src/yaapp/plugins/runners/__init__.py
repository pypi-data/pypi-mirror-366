"""
Runner plugins for yaapp.

Runners are plugins that provide different execution backends for yaapp applications.
Each runner implements the standard plugin protocol with help() and run() methods.

Available runners:
- click: Default CLI runner with interactive shell capabilities
- server: FastAPI web server with auto-generated endpoints  
- rich: Beautiful console TUI with tables and rich formatting
- prompt: Auto-completing TUI with prompt_toolkit
- typer: Simple interactive TUI with basic features

Runners are automatically discovered by scanning the plugins/runners/ directory.
Each runner uses @yaapp.expose("runner_name") decorator for auto-registration.
No manual imports needed - the discovery system finds all runners dynamically.
"""