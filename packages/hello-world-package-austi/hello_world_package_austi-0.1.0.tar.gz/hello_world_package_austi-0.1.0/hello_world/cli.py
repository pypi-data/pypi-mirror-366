"""
Command line interface for the hello world package.
"""

import argparse
from hello_world import greet


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="A simple hello world CLI")
    parser.add_argument(
        "name", 
        nargs="?", 
        help="Name to greet (optional)"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version="hello-world-package 0.1.0"
    )
    
    args = parser.parse_args()
    greet(args.name)


if __name__ == "__main__":
    main()
