# gh-templates

GitHub Templates CLI tool for managing and using GitHub repository templates.

## Installation

```bash
pip install gh-templates
```

## Usage

```bash
gh-templates --help
gh-templates --version
```

## Platform Support

This package automatically installs the correct binary for your platform:

- **Linux**: x64, ARM64 (glibc and musl)
- **macOS**: x64 (Intel), ARM64 (Apple Silicon)
- **Windows**: x64

## How it Works

This is a unified installer package that:

1. Detects your platform during installation
2. Installs the appropriate platform-specific package as a dependency
3. Provides a unified `gh-templates` command that delegates to the platform binary

## License

Apache-2.0
