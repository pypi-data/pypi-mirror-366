# Vibe Framework

A lightweight Python framework for quick project setup, similar to Django but simpler.

## Installation

### Install from source (development)

```bash
poetry install
```

### Install as a package

Once published to PyPI, you can install with:

```bash
pip install vibe-framework
```

## Quick Start

### Create a new project

```bash
# Create project in current directory
vibe init

# Or create project in a new directory
vibe init myproject
```

This creates:
- `main.py` - Your main application file
- `tests/` - Test directory with example tests
- `pytest.ini` - Pytest configuration
- `requirements.txt` - Python dependencies

### Run your project

```bash
vibe
```

This executes your `main.py` file.

### Run tests

```bash
vibe test
```

This runs all tests in the `tests/` directory using pytest.

## Commands

- `vibe` - Run the main.py file in the current directory
- `vibe init [project_name]` - Initialize a new vibe project
- `vibe test` - Run tests using pytest

## Example

See `example_main.py` for a simple example of a main.py file that works with vibe.

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting and Linting

This project uses pre-commit hooks for code quality. To set up:

```bash
poetry run pre-commit install
```

The following tools are configured:
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting

### Manual Formatting

```bash
poetry run black src tests
poetry run isort src tests
poetry run flake8 src tests
```

## License

MIT License - see LICENSE file for details.