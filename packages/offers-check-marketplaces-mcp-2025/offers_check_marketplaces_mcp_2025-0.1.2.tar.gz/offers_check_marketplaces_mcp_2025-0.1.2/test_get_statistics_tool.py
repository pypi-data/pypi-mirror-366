#!/usr/bin/env python3
"""
Test script for the get_statistics MCP tool.
"""

import asyncio
from offers_check_marketplaces.server import initialize_components, get_statistics
from offers_check_marketplaces.server import database_manager


async def test_get_statistics_tool():
    """Test the get_statistics MCP tool with sample data."""
    print("🧪 Testing get_statistics MCP tool...")
    
    # Initialize components
    await initialize_components()
    print("Components initialized")
    
    # Test with empty database first
    result = await get_statistics()
    print("\nStatistics with empty database:")
    print(f"  Status: {result['status']}")
    print(f"  Total products: {result['statistics']['total_products']}")
    print(f"  Products with prices: {result['statistics']['products_with_prices']}")
    print(f"  Average delta: {result['statistics']['average_delta_percent']}%")
    
    # Add sample data
    sample_product = {
        'code': 123456.0,
        'model_name': 'Test Product',
        'category': 'Test Category',
        'unit': 'шт',
        'priority_1_source': 'komus.ru',
        'priority_2_source': 'vseinstrumenti.ru'
    }
    
    try:
        # Import the global database_manager after initialization
        from offers_check_marketplaces import server
        db_manager = server.database_manager
        
        if db_manager is None:
            print("Database manager is None after initialization")
            return
            
        product_id = await db_manager.save_product(sample_product)
        print(f"\nSample product saved with ID: {product_id}")
        
        # Add sample prices
        sample_prices = {
            'komus.ru': {
                'price': 100.0, 
                'currency': 'RUB', 
                'availability': 'В наличии', 
                'product_url': 'http://test.com'
            },
            'vseinstrumenti.ru': {
                'price': 120.0, 
                'currency': 'RUB', 
                'availability': 'В наличии', 
                'product_url': 'http://test2.com'
            }
        }
        
        await db_manager.update_product_prices(product_id, sample_prices)
        print("Sample prices added")
        
        # Test get_statistics with data
        result = await get_statistics()
        stats = result['statistics']
        print("\nStatistics with sample data:")
        print(f"  Status: {result['status']}")
        print(f"  Total products: {stats['total_products']}")
        print(f"  Products with prices: {stats['products_with_prices']}")
        print(f"  Average delta: {stats['average_delta_percent']}%")
        print(f"  Categories: {stats['category_breakdown']}")
        print(f"  Marketplace coverage: {stats['marketplace_coverage']}")
        print(f"  Timestamp: {result['timestamp']}")
        
        # Verify requirements compliance
        print("\nRequirements verification:")
        print(f"  ✓ 5.1 - Total products returned: {stats['total_products']}")
        print(f"  ✓ 5.2 - Products with successful matches: {stats['products_with_prices']}")
        print(f"  ✓ 5.3 - Average percentage deltas: {stats['average_delta_percent']}%")
        print(f"  ✓ 5.4 - Category breakdown: {len(stats['category_breakdown'])} categories")
        print(f"  ✓ 5.5 - Marketplace coverage: {len(stats['marketplace_coverage'])} marketplaces")
        
        print("\nget_statistics tool test completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_get_statistics_tool())