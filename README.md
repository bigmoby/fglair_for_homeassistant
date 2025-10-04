# FGLair&trade; integration for homeassistant

[![GitHub Release][releases-shield]][releases]
![Project Stage][project-stage-shield]
[![License][license-shield]](LICENSE.md)

![Maintenance][maintenance-shield]
[![GitHub Activity][commits-shield]][commits]

[![Donate](https://img.shields.io/badge/donate-BuyMeCoffee-yellow.svg)](https://www.buymeacoffee.com/bigmoby)

![FGLAIR_LOGO](FGLair_logo.png)

This is a platform to support Fujitsu General Airconditioners under Climate component of Home Assistant. The Python supporting library for accessing the FGLair&trade; API is located at: https://github.com/bigmoby/pyfujitsugeneral/

## Sample UI:

![UI_SCREENSHOT1](Capture.PNG)
![UI_SCREENSHOT2](Capture2.PNG)

## Installation

### Manual

1. Create this directory path `custom_components/fglair_heatpump_controller/` if it does not already exist.

2. Download the all `custom_components/fglair_heatpump_controller/` files from the repo and place it in the directory mentioned in previous step.

### HACS

1. Add this repository to HACS:

```
https://github.com/bigmoby/fglair_for_homeassistant
```

2. Search for the `FGLair integration for homeassistant` integration and choose install.

3. Reboot Home Assistant.

## Usage:

In Home Assistant->Settings->Device & services->Integration menu add the new integration FGLair and configure it.

Please, use your FGLair app username/password and region your FGLair account is registered (choose one of `region`: `eu`, `cn` or `us`). For `tokenpath` field you could leave the default value `token.txt`. You could set a proper `temperature_offset`, default will be `0`.

Attention: please, remove from `configuration.yaml` any previous FGLair installation setup.

Note for A/C units with horizontal swing support, the horizontal swing and position can be changed but only the vertical position will be shown due to limitations with Home Assistant's climate entity.

## Develop

### Quick Start

Setup the development environment:

```bash
make setup
```

Or manually:

```bash
./scripts/setup
```

### Available Commands

Use the Makefile for common development tasks:

```bash
make help          # Show all available commands
make setup         # Setup development environment
make test          # Run tests
make test-coverage # Run tests with coverage report
make lint          # Run linting tools
make format        # Format code
make check         # Run all checks (lint + test)
make clean         # Clean up temporary files
make install-dev   # Install in development mode
make develop       # Start development server
make ci            # Run CI pipeline locally

# Pre-commit system
make pre-commit-install          # Install pre-commit hooks
make pre-commit-uninstall        # Uninstall pre-commit hooks
make pre-commit-run              # Run pre-commit on all files
```

### Development Tools

This project includes development tools for code quality and testing:

#### Pre-Commit Hooks

Install pre-commit hooks to automatically run checks before commits:

```bash
make pre-commit-install  # Install pre-commit hooks
```

The pre-commit configuration includes:

- ✅ Code formatting with ruff
- ✅ Linting with ruff and flake8
- ✅ Type checking with mypy
- ✅ Test execution with pytest
- ✅ Coverage checking (minimum 100%)

#### Manual Commands

Activate virtual environment:

```bash
source venv/bin/activate
```

Run tests:

```bash
python -m pytest tests/ -v
```

Run linting:

```bash
pre-commit run --all-files
```

Start development server:

```bash
./scripts/develop
```

### Dependencies Structure

- `requirements.txt` - Core runtime dependencies
- `requirements.test.txt` - Testing and development dependencies
- `pyproject.toml` - Project metadata and optional dependencies

The project uses:

- **pyfujitsugeneral==2.0.33** - Core API client for FGLair
- **aiofiles==24.1.0** - Async file operations
- **pytest-homeassistant-custom-component** - Testing framework for HA integrations
- **ruff** - Fast Python linter and formatter
- **mypy** - Static type checker
- **pre-commit** - Git hooks for code quality

## Known issues and missing features:

- [x] Logging needs to be implemented
- [x] The “powerful” functionality is implemented via the preset selections in the UI
- [ ] There are some other functionalities in the A/C which currently is not implemented.
- [ ] Possibility to add external temperature sensor

##

\*\* "FGLair" is a trademark of FUJITSU GENERAL LIMITED.

[releases-shield]: https://img.shields.io/github/release/bigmoby/fglair_for_homeassistant.svg
[releases]: https://github.com/bigmoby/fglair_for_homeassistant/releases
[project-stage-shield]: https://img.shields.io/badge/project%20stage-production%20ready-brightgreen.svg
[license-shield]: https://img.shields.io/github/license/bigmoby/fglair_for_homeassistant
[maintenance-shield]: https://img.shields.io/maintenance/yes/2025.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/bigmoby/fglair_for_homeassistant.svg
[commits]: https://img.shields.io/github/commits/bigmoby/fglair_for_homeassistant
