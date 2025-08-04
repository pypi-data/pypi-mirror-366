"""
Entry point for running hyperliquid-mcp as a module.
Enables usage like: python -m hyperliquid_mcp or uvx hyperliquid-mcp
"""

from .server import main

def main_entry():
    """Main entry point for uvx and CLI usage"""
    main()

if __name__ == "__main__":
    main_entry()