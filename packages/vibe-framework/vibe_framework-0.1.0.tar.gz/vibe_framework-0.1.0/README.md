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

## Usage

After installing vibe, you can use it in any Python project:

1. Create a `main.py` file in your project directory:

```python
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
```

2. Run the vibe command:

```bash
vibe
```

This will execute your `main.py` file. Vibe looks for a `main.py` file in the current directory and runs it.

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