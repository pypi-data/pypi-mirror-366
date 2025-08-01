# tfmate

**Documentation**: <https://tfmate-ads.readthedocs.org>

`tfmate` is a command line interface and Python library for analyzing Terraform configurations and state files. It provides powerful tools for understanding your infrastructure as code, including configuration analysis, AWS service discovery, and state file inspection.

## Features

- **Configuration Analysis**: Analyze Terraform configuration files to understand providers, backends, and version constraints
- **AWS Service Discovery**: List and filter AWS services from botocore definitions
- **State File Inspection**: Extract Terraform version and metadata from state files
- **Multiple Output Formats**: Support for JSON, table, and text output formats
- **Flexible Configuration**: Customizable through configuration files and environment variables

## Installation

`tfmate` supports Python 3.10+.

To install from PyPI:

```shell
pip install tfmate
```

To install using `uv`:

```shell
    sh -c "$(curl -fsSL https://astral.sh/uv/install)"
    uv tool install tfmate
```

Ensure you have `./local/bin` in your `PATH`, since that's where `uv` puts the
executable.

## Quick Start

```bash
# Get help
tfmate --help

# Analyze Terraform configuration
tfmate analyze config

# List AWS services
tfmate aws services

# Get Terraform version from state
tfmate terraform version

# Use JSON output for scripting
tfmate --output json analyze config
```

## Usage Examples

### Analyze Terraform Configuration

```bash
# Analyze current directory
tfmate analyze config

# Analyze specific directory with detailed info
tfmate analyze config --directory ./infrastructure --show-providers --show-backend

# Output as JSON for scripting
tfmate --output json analyze config > config.json
```

### AWS Service Discovery

```bash
# List all AWS services
tfmate aws services

# List only service names
tfmate aws services --names-only

# Filter services by pattern
tfmate aws services --filter-name "ec2*" --sort-by name
```

### State File Operations

```bash
# Get Terraform version from state
tfmate terraform version

# Get version from specific directory
tfmate terraform version --directory ./infrastructure

# Use explicit state file (local only)
tfmate terraform version --state-file ./terraform.tfstate
```

## Documentation

For detailed documentation, visit: <https://tfmate.readthedocs.org>

- [Installation Guide](https://tfmate.readthedocs.org/en/latest/overview/installation.html)
- [Quickstart Guide](https://tfmate.readthedocs.org/en/latest/overview/quickstart.html)
- [Usage Guide](https://tfmate.readthedocs.org/en/latest/overview/usage.html)
- [Configuration Guide](https://tfmate.readthedocs.org/en/latest/overview/configuration.html)

## Development

To set up a development environment:

```bash
# Clone the repository
git clone https://github.com/cmalek/terraform-common-modules.git
cd tfmate

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Run tests
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
