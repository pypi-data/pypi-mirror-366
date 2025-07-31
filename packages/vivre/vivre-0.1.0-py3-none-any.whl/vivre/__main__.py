"""
Command-line interface for the vivre package.

This module allows the vivre package to be executed directly:
    python -m vivre [command] [options]
"""

from .cli import app

if __name__ == "__main__":
    app()
