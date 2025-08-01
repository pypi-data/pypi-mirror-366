#!/usr/bin/env python3
"""
Quick test to verify server initialization works properly.
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path.cwd()))

from offers_check_marketplaces.server import initialize_components, APP_ID

async def test_initialization():
    """Test that all components can be initialized properly."""
    print(f"Testing MCP server: {APP_ID}")
    print("Attempting to initialize components...")
    
    try:
        await initialize_components()
        print("All components initialized successfully!")
        return True
    except Exception as e:
        print(f"Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_initialization())
    sys.exit(0 if success else 1)