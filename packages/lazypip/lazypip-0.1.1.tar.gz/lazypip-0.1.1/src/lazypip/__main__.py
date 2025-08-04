#!/usr/bin/env python3
"""
LazyPip - A lazygit-style TUI for Python package management

Main entry point for the application.
"""

import sys
import os
from pathlib import Path

from .app import LazypipApp


def main():
    """Main entry point for LazyPip."""
    try:
        import subprocess
        result = subprocess.run(["pip", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Error: pip is not installed or not available in PATH")
            print("Please install pip and try again.")
            sys.exit(1)
    except FileNotFoundError:
        print("Error: pip command not found")
        print("Please ensure pip is installed and available in your PATH")
        sys.exit(1)

    app = LazypipApp()

    try:
        app.run()
    except KeyboardInterrupt:
        print("\nThanks for using LazyPip!")
        sys.exit(0)
    except Exception as e:
        print(f"Error running LazyPip: {e}")
        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
