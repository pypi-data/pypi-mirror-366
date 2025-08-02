"""CLI for vibe framework."""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def init_project(project_name=None):
    """Initialize a new vibe project."""
    if project_name:
        # Create project directory
        project_dir = Path(project_name)
        if project_dir.exists():
            print(f"Error: Directory '{project_name}' already exists.")
            sys.exit(1)
        project_dir.mkdir()
        os.chdir(project_dir)
    
    # Create main.py
    main_content = '''"""Main module for vibe project."""


def main():
    """Main function."""
    print("Hello, World!")


if __name__ == "__main__":
    main()
'''
    
    with open("main.py", "w") as f:
        f.write(main_content)
    
    # Create tests directory
    tests_dir = Path("tests")
    tests_dir.mkdir(exist_ok=True)
    
    # Create __init__.py in tests
    (tests_dir / "__init__.py").touch()
    
    # Create sample test file
    test_content = '''"""Test module for vibe project."""

import pytest
from main import main


def test_main(capsys):
    """Test the main function."""
    main()
    captured = capsys.readouterr()
    assert "Hello, World!" in captured.out


def test_example():
    """Example test to demonstrate pytest."""
    assert 1 + 1 == 2
    assert "hello".upper() == "HELLO"
    assert len([1, 2, 3]) == 3
'''
    
    with open(tests_dir / "test_main.py", "w") as f:
        f.write(test_content)
    
    # Create pytest configuration
    pytest_ini = '''[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
'''
    
    with open("pytest.ini", "w") as f:
        f.write(pytest_ini)
    
    # Create requirements.txt
    requirements = '''pytest>=7.0.0
'''
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print(f"✨ Created new vibe project{f' in {project_name}' if project_name else ''}!")
    print("\nProject structure:")
    print("  main.py          - Main entry point")
    print("  tests/           - Test directory")
    print("  └── test_main.py - Example test file")
    print("  pytest.ini       - Pytest configuration")
    print("  requirements.txt - Python dependencies")
    print("\nNext steps:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run your project: vibe")
    print("  3. Run tests: vibe test")


def run_tests():
    """Run tests using pytest."""
    try:
        # Try to import pytest to check if it's installed
        import pytest
    except ImportError:
        print("Error: pytest is not installed.")
        print("Install it with: pip install pytest")
        print("Or install all requirements: pip install -r requirements.txt")
        sys.exit(1)
    
    # Run pytest
    exit_code = pytest.main(["-v"])
    sys.exit(exit_code)


def run_project():
    """Run the main.py file."""
    if not os.path.exists("main.py"):
        print("Error: No main.py file found in current directory.")
        print("Create a new project with: vibe init")
        sys.exit(1)
    
    # Execute main.py
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running main.py: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def main():
    """Main entry point for vibe command."""
    parser = argparse.ArgumentParser(
        description="Vibe - A lightweight Python framework",
        prog="vibe"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new vibe project")
    init_parser.add_argument(
        "project_name",
        nargs="?",
        help="Name of the project directory to create (optional)"
    )
    
    # Test command
    subparsers.add_parser("test", help="Run tests using pytest")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "init":
        init_project(args.project_name)
    elif args.command == "test":
        run_tests()
    else:
        # Default behavior - run the project
        run_project()


if __name__ == "__main__":
    main()