# yaapp - Yet Another App Framework

A powerful Python framework for building CLI and web applications with plugin-based architecture.

## 🚀 Quick Start

### Try the Auth Plugin Demo
```bash
# Interactive demo launcher
./examples/plugins/auth/auth-demo.sh

# Or run directly
./examples/plugins/auth/quick-start.sh           # Basic operations
python examples/plugins/auth/workflow.py         # Complete demo (Python)
./examples/plugins/auth/workflow.sh              # Complete demo (Shell)
```

### Examples
- **Auth Plugin**: `examples/plugins/auth/` - Complete authentication & authorization
- **Storage Plugin**: `examples/plugins/storage/` - Data persistence
- **Issues Plugin**: `examples/plugins/issues/` - Issue tracking

## 📖 Documentation

- **[Development Guide](docs/development.md)** - How to develop with yaapp
- **[Design Documentation](docs/design.md)** - Architecture and design decisions
- **[Testing Guide](docs/testing.md)** - Testing strategies and examples

## 🔧 Installation

```bash
# Install from source
pip install -e .

# For CLI support
pip install click

# For web server support
pip install fastapi uvicorn
```

## 📁 Project Structure

```
yaapp/
├── src/yaapp/           # Core framework
├── examples/            # Example applications
│   └── plugins/         # Plugin examples
│       ├── auth/        # Authentication & authorization
│       ├── storage/     # Data persistence
│       └── issues/      # Issue tracking
├── tests/               # Test suites
└── docs/                # Documentation
```

## 🎯 Features

- **Plugin Architecture**: Modular, extensible design
- **Auto-Discovery**: Automatic plugin detection and configuration
- **Dual Interface**: Both CLI and web API from the same code
- **Type Safety**: Full type hints and validation
- **Configuration**: JSON/YAML configuration with environment variables
- **Storage**: Multiple backends (memory, file, SQLite)
- **Authentication**: Built-in auth and authorization
- **Testing**: Comprehensive test framework

## 🤝 Contributing

See the development guide in `docs/development.md` for contribution guidelines.

## 📄 License

[Add your license here]