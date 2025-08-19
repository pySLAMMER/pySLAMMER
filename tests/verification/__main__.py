#!/usr/bin/env python3
"""
Entry point for verification module when run as a module.

Usage:
    python -m verification <command> [options]
    uv run python -m verification <command> [options]
"""

from .cli import cli

if __name__ == '__main__':
    cli()