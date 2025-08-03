"""
Main entry point for the offers_check_marketplaces MCP application.
This file simply imports and runs the main function from the server module.
"""
import sys
from offers_check_marketplaces.server import main

if __name__ == "__main__":
    sys.exit(main())