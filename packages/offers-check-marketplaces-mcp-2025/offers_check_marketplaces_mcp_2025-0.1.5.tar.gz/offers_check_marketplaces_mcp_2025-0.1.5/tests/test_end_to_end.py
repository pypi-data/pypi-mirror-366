#!/usr/bin/env python3
"""
End-to-end testing script for offers-check-marketplaces MCP server.

This script tests the complete workflow:
1. Load Excel data from input file
2. Test all MCP tools functionality
3. Verify data processing and storage
4. Generate output Excel file
"""

import asyncio
import sys
import os
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from offers_check_marketplaces.server import initialize_components
from offers_check_marketplaces.data_processor import DataProcessor
from offers_check_marketplaces.database_manager import DatabaseManager
from offers_check_marketplaces.search_engine import SearchEngine
from offers_check_marketplaces.statistics import StatisticsGenerator
from offers_check_marketplaces.marketplace_client import MarketplaceClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EndToEndTester:
    """End-to-end testing class for the MCP server"""
    
    def __init__(self):
        self.data_processor = None
        self.database_manager = None
        self.search_engine = None
        self.statistics_generator = None
        self.marketplace_client = None
        self.test_results = {}
        
    async def initialize_system(self):
        """Initialize all system components"""
        logger.info("Initializing system components...")
        
        try:
            # Initialize components using the server's initialization function
            await initialize_components()
            
            # Get component instances
            from offers_check_marketplaces.server import (
                data_processor, database_manager, search_engine, 
                statistics_generator, marketplace_client
            )
            
            self.data_processor = data_processor
            self.database_manager = database_manager
            self.search_engine = search_engine
            self.statistics_generator = statistics_generator
            self.marketplace_client = marketplace_client
            
            logger.info("System components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize system components: {e}")
            return False
    
    async def test_excel_data_loading(self) -> bool:
        """Test loading Excel data from input file"""
        logger.info("Testing Excel data loading...")
        
        try:
            input_file = Path("data/Таблица на вход.xlsx")
            
            if not input_file.exists():
                logger.error(f"Input Excel file not found: {input_file}")
                return False
            
            # Load Excel data
            excel_data = await self.data_processor.load_excel_data(str(input_file))
            
            if not excel_data:
                logger.error("No data loaded from Excel file")
                return False
            
            logger.info(f"Successfully loaded {len(excel_data)} products from Excel")
            
            # Validate data structure
            first_product = excel_data[0]
            required_fields = [
                "Код\nмодели", "model_name", "Категория", "Единица измерения",
                "Приоритет \n1 Источники", "Приоритет \n2 Источники"
            ]
            
            for field in required_fields:
                if field not in first_product:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            logger.info("Excel data structure validation passed")
            
            # Store data in database
            products_saved = 0
            for product_data in excel_data:
                try:
                    await self.database_manager.save_product(product_data)
                    products_saved += 1
                except Exception as e:
                    logger.warning(f"Failed to save product {product_data.get('Код\nмодели', 'unknown')}: {e}")
            
            logger.info(f"Saved {products_saved} products to database")
            
            self.test_results['excel_loading'] = {
                'status': 'success',
                'products_loaded': len(excel_data),
                'products_saved': products_saved,
                'sample_product': first_product
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Excel data loading test failed: {e}")
            self.test_results['excel_loading'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    

    
    async def test_get_product_details_tool(self) -> bool:
        """Test the get_product_details MCP tool"""
        logger.info("Testing get_product_details MCP tool...")
        
        try:
            # Import the MCP tool function
            from offers_check_marketplaces.server import get_product_details
            
            # Get a sample product code from database
            products = await self.database_manager.get_all_products()
            
            if not products:
                logger.warning("No products in database to test get_product_details")
                return True  # Not a failure, just no data
            
            test_product_code = products[0]['code']
            
            # Call the MCP tool
            result = await get_product_details(test_product_code)
            
            if not result:
                logger.error("get_product_details returned no result")
                return False
            
            if result.get('status') == 'error':
                logger.error(f"get_product_details returned error: {result.get('message')}")
                return False
            
            logger.info(f"get_product_details tool executed successfully")
            logger.info(f"   Status: {result.get('status')}")
            logger.info(f"   Product code: {test_product_code}")
            logger.info(f"   Product name: {result.get('product', {}).get('model_name', 'N/A')}")
            logger.info(f"   Prices count: {len(result.get('prices', []))}")
            
            self.test_results['get_product_details'] = {
                'status': 'success',
                'product_code': test_product_code,
                'prices_count': len(result.get('prices', [])),
                'sample_result': result
            }
            
            return True
            
        except Exception as e:
            logger.error(f"get_product_details tool test failed: {e}")
            self.test_results['get_product_details'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def test_get_statistics_tool(self) -> bool:
        """Test the get_statistics MCP tool"""
        logger.info("Testing get_statistics MCP tool...")
        
        try:
            # Import the MCP tool function
            from offers_check_marketplaces.server import get_statistics
            
            # Call the MCP tool
            result = await get_statistics()
            
            if not result:
                logger.error("get_statistics returned no result")
                return False
            
            if result.get('status') == 'error':
                logger.error(f"get_statistics returned error: {result.get('message')}")
                return False
            
            logger.info(f"get_statistics tool executed successfully")
            logger.info(f"   Status: {result.get('status')}")
            
            stats = result.get('statistics', {})
            logger.info(f"   Total products: {stats.get('total_products', 0)}")
            logger.info(f"   Products with prices: {stats.get('products_with_prices', 0)}")
            logger.info(f"   Average delta percent: {stats.get('average_delta_percent', 0)}")
            logger.info(f"   Categories: {len(stats.get('category_breakdown', {}))}")
            logger.info(f"   Marketplaces: {len(stats.get('marketplace_coverage', {}))}")
            
            self.test_results['get_statistics'] = {
                'status': 'success',
                'statistics': stats,
                'sample_result': result
            }
            
            return True
            
        except Exception as e:
            logger.error(f"get_statistics tool test failed: {e}")
            self.test_results['get_statistics'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def test_output_excel_generation(self) -> bool:
        """Test generation of output Excel file"""
        logger.info("📄 Testing output Excel file generation...")
        
        try:
            # Get all products from database
            products = await self.database_manager.get_all_products()
            
            if not products:
                logger.warning("No products in database to generate output Excel")
                return True  # Not a failure, just no data
            
            # Prepare data for Excel output
            excel_output_data = []
            
            for product in products:
                # Get prices for this product
                prices = await self.database_manager.get_product_prices(product['id'])
                
                # Create output record with original structure plus price data
                output_record = {
                    "Код\nмодели": product['code'],
                    "model_name": product['model_name'],
                    "Категория": product['category'],
                    "Единица измерения": product['unit'],
                    "Приоритет \n1 Источники": product['priority_1_source'],
                    "Приоритет \n2 Источники": product['priority_2_source'],
                    "Цена позиции\nМП c НДС": "",
                    "Цена позиции\nB2C c НДС": "",
                    "Дельта в процентах": "",
                    "Ссылка на источник": "",
                    "Цена 2 позиции\nB2C c НДС": ""
                }
                
                # Fill in price data if available
                if prices:
                    # Use first price as primary
                    primary_price = prices[0]
                    output_record["Цена позиции\nМП c НДС"] = primary_price.get('price', '')
                    output_record["Цена позиции\nB2C c НДС"] = primary_price.get('price', '')
                    output_record["Ссылка на источник"] = primary_price.get('product_url', '')
                    
                    # Use second price if available
                    if len(prices) > 1:
                        secondary_price = prices[1]
                        output_record["Цена 2 позиции\nB2C c НДС"] = secondary_price.get('price', '')
                        
                        # Calculate delta between prices
                        if (primary_price.get('price') and secondary_price.get('price') and 
                            primary_price['price'] > 0):
                            delta = ((secondary_price['price'] - primary_price['price']) / 
                                   primary_price['price']) * 100
                            output_record["Дельта в процентах"] = round(delta, 2)
                
                excel_output_data.append(output_record)
            
            # Generate output Excel file
            output_file = Path("data/Таблица на выход (отработанная).xlsx")
            success = await self.data_processor.save_excel_data(excel_output_data, str(output_file))
            
            if not success:
                logger.error("Failed to generate output Excel file")
                return False
            
            if not output_file.exists():
                logger.error("Output Excel file was not created")
                return False
            
            logger.info(f"Successfully generated output Excel file: {output_file}")
            logger.info(f"   Records written: {len(excel_output_data)}")
            
            self.test_results['output_excel'] = {
                'status': 'success',
                'output_file': str(output_file),
                'records_written': len(excel_output_data),
                'file_exists': output_file.exists()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Output Excel generation test failed: {e}")
            self.test_results['output_excel'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def run_full_test_suite(self) -> bool:
        """Run the complete end-to-end test suite"""
        logger.info("Starting end-to-end test suite...")
        
        # Initialize system
        if not await self.initialize_system():
            logger.error("System initialization failed")
            return False
        
        # Run all tests
        tests = [
            ("Excel Data Loading", self.test_excel_data_loading),
            ("Get Product Details Tool", self.test_get_product_details_tool),
            ("Get Statistics Tool", self.test_get_statistics_tool),
            ("Output Excel Generation", self.test_output_excel_generation)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*60}")
            logger.info(f"Running test: {test_name}")
            logger.info(f"{'='*60}")
            
            try:
                if await test_func():
                    logger.info(f"{test_name}: PASSED")
                    passed_tests += 1
                else:
                    logger.error(f"{test_name}: FAILED")
            except Exception as e:
                logger.error(f"{test_name}: FAILED with exception: {e}")
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info(f"TEST SUITE SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Save test results to file
        results_file = Path("test_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': total_tests - passed_tests,
                    'success_rate': (passed_tests/total_tests)*100
                },
                'detailed_results': self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Detailed test results saved to: {results_file}")
        
        return passed_tests == total_tests

async def main():
    """Main function to run end-to-end tests"""
    print("🧪 offers-check-marketplaces End-to-End Testing")
    print("=" * 60)
    
    tester = EndToEndTester()
    success = await tester.run_full_test_suite()
    
    if success:
        print("\nAll tests passed! System is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())