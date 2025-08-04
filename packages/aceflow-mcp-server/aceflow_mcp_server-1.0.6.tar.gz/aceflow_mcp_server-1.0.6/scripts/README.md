# Scripts

This directory contains build, deployment, and development scripts for AceFlow MCP Server.

## Directory Structure

### `build/`
Scripts for building and packaging the project:
- `build_package.py` - Build Python package
- `check_publish_readiness.py` - Verify package is ready for publishing

### `deploy/`
Scripts for deployment and publishing:
- `build_and_publish.sh` - Complete build and publish workflow
- `deploy_to_pypi.sh` - Deploy package to PyPI
- `setup_pypi_auth.sh` - Configure PyPI authentication

### `dev/`
Development and testing utilities:
- `setup_environment.sh` - Set up development environment
- `test_before_publish.sh` - Run tests before publishing
- `test_uvx_install.sh` - Test uvx installation
- `diagnose_mcp.sh` - Diagnose MCP connection issues

## Usage

### Building the Package
```bash
python scripts/build/build_package.py
```

### Publishing to PyPI
```bash
./scripts/deploy/deploy_to_pypi.sh
```

### Setting up Development Environment
```bash
./scripts/dev/setup_environment.sh
```

## Requirements

- Python 3.8+
- pip and build tools
- PyPI account (for publishing)
- uvx (for testing)