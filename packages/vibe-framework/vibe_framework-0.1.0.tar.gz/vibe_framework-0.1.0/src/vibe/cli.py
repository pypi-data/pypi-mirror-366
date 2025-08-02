"""CLI for vibe framework."""

import os
import subprocess
import sys


def main():
    """Main entry point for vibe command."""
    # Check if main.py exists in current directory
    if not os.path.exists("main.py"):
        print("Error: No main.py file found in current directory.")
        print("Create a main.py file to use with vibe.")
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


if __name__ == "__main__":
    main()