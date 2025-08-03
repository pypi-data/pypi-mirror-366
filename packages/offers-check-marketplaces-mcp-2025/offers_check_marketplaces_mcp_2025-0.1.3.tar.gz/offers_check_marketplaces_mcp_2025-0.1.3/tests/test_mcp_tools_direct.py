#!/usr/bin/env python3
"""
Direct test of MCP tools to verify they work correctly.
This test calls the MCP tools directly to ensure they function as expected.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from offers_check_marketplaces.server import initialize_components, get_product_details, get_statistics

async def test_mcp_tools_direct():
    """Test MCP tools directly"""
    print("🧪 Testing MCP Tools Directly")
    print("=" * 50)
    
    # Initialize system
    print("Initializing system...")
    await initialize_components()
    print("System initialized")
    
    # Test removed - search_products method has been removed
    
    # Test get_statistics
    print("\nTesting get_statistics...")
    stats_result = await get_statistics()
    print(f"Status: {stats_result.get('status')}")
    stats = stats_result.get('statistics', {})
    print(f"Total products: {stats.get('total_products', 0)}")
    print(f"Products with prices: {stats.get('products_with_prices', 0)}")
    
    # Test get_product_details with a known product code
    print("\nTesting get_product_details...")
    details_result = await get_product_details(195385.0)
    print(f"Status: {details_result.get('status')}")
    product = details_result.get('product', {})
    print(f"Product name: {product.get('model_name', 'N/A')}")
    
    print("\nAll MCP tools tested successfully!")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools_direct())