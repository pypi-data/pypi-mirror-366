#!/usr/bin/env python3
"""
Comprehensive test for centralized error handling in offers-check-marketplaces.

Tests all error handling decorators, graceful degradation, and user-friendly error messages.
"""

import asyncio
import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from offers_check_marketplaces.error_handling import (
    ErrorHandler,
    ErrorCategory,
    ErrorSeverity,
    MarketplaceUnavailableError,
    ScrapingError,
    DatabaseError,
    ValidationError,
    DataProcessingError,
    handle_errors,
    handle_marketplace_errors,
    handle_database_errors,
    handle_validation_errors,
    create_user_friendly_error,
    error_handler,
    log_recovery_attempt
)

from offers_check_marketplaces.database_manager import DatabaseManager
from offers_check_marketplaces.data_processor import DataProcessor
from offers_check_marketplaces.marketplace_client import MarketplaceClient
from offers_check_marketplaces.search_engine import SearchEngine
from offers_check_marketplaces.statistics import StatisticsGenerator


class TestErrorHandling:
    """Test suite for centralized error handling."""

    def setup_method(self):
        """Setup for each test method."""
        # Reset error handler stats
        global error_handler
        error_handler = ErrorHandler()

    def test_error_handler_initialization(self):
        """Test that error handler initializes correctly."""
        handler = ErrorHandler()
        assert handler.error_stats["total_errors"] == 0
        assert len(handler.error_history) == 0
        assert handler.max_history_size == 1000

    def test_error_logging(self):
        """Test error logging functionality."""
        test_error = ValueError("Test error")
        
        error_info = error_handler.log_error(
            error=test_error,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            component="test_component",
            details={"test": "data"},
            recovery_action="Test recovery"
        )
        
        assert error_info.error_type == "ValueError"
        assert error_info.message == "Test error"
        assert error_info.category == ErrorCategory.VALIDATION
        assert error_info.severity == ErrorSeverity.MEDIUM
        assert error_info.component == "test_component"
        assert error_info.recovery_action == "Test recovery"
        
        # Check stats update
        assert error_handler.error_stats["total_errors"] == 1
        assert error_handler.error_stats["errors_by_category"]["validation"] == 1
        assert error_handler.error_stats["errors_by_component"]["test_component"] == 1

    def test_marketplace_error_types(self):
        """Test marketplace-specific error types."""
        # Test MarketplaceUnavailableError
        error = MarketplaceUnavailableError("komus.ru", "Connection timeout")
        assert error.marketplace == "komus.ru"
        assert error.reason == "Connection timeout"
        assert error.recoverable is True
        assert "komus.ru" in str(error)
        
        # Test ScrapingError
        error = ScrapingError("ozon.ru", "https://ozon.ru/search", "Invalid selector")
        assert error.marketplace == "ozon.ru"
        assert error.url == "https://ozon.ru/search"
        assert error.reason == "Invalid selector"
        assert error.recoverable is True

    def test_database_error_types(self):
        """Test database-specific error types."""
        error = DatabaseError("Connection failed", operation="save_product")
        assert error.operation == "save_product"
        assert error.recoverable is True
        assert "Connection failed" in str(error)

    def test_validation_error_types(self):
        """Test validation-specific error types."""
        error = ValidationError("Invalid product code", field="code", value="invalid")
        assert error.field == "code"
        assert error.value == "invalid"
        assert "Invalid product code" in str(error)

    def test_handle_errors_decorator_sync(self):
        """Test handle_errors decorator with synchronous function."""
        @handle_errors(
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            component="test",
            return_on_error="error_result"
        )
        def test_function():
            raise ValueError("Test error")
        
        result = test_function()
        assert result == "error_result"
        assert error_handler.error_stats["total_errors"] == 1

    async def test_handle_errors_decorator_async(self):
        """Test handle_errors decorator with asynchronous function."""
        @handle_errors(
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            component="test",
            return_on_error={"status": "error"}
        )
        async def test_async_function():
            raise RuntimeError("Async test error")
        
        result = await test_async_function()
        assert result == {"status": "error"}
        assert error_handler.error_stats["total_errors"] == 1

    async def test_handle_marketplace_errors_decorator(self):
        """Test marketplace error handling decorator."""
        @handle_marketplace_errors(marketplace="test.ru", graceful_degradation=True)
        async def test_marketplace_function():
            raise MarketplaceUnavailableError("test.ru", "Service down")
        
        result = await test_marketplace_function()
        assert result["marketplace"] == "test.ru"
        assert result["product_found"] is False
        assert result["recoverable"] is True
        assert "Service down" in result["error"]

    async def test_handle_database_errors_decorator(self):
        """Test database error handling decorator with retries."""
        call_count = 0
        
        @handle_database_errors(operation="test_operation", retry_count=2, retry_delay=0.1)
        async def test_database_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("Database connection failed")
            return "success"
        
        result = await test_database_function()
        assert result == "success"
        assert call_count == 3  # Initial call + 2 retries

    def test_handle_validation_errors_decorator(self):
        """Test validation error handling decorator."""
        @handle_validation_errors(component="test", return_default=None)
        def test_validation_function():
            raise ValidationError("Invalid input", field="test_field")
        
        result = test_validation_function()
        assert result is None
        assert error_handler.error_stats["total_errors"] == 1

    def test_create_user_friendly_error_marketplace(self):
        """Test user-friendly error creation for marketplace errors."""
        error = MarketplaceUnavailableError("komus.ru", "Connection timeout")
        result = create_user_friendly_error(error, "поиск товаров")
        
        assert result["status"] == "error"
        assert result["error_code"] == "MARKETPLACE_UNAVAILABLE"
        assert result["recoverable"] is True
        assert result["retry_suggested"] is True
        assert "komus.ru" in result["message"]

    def test_create_user_friendly_error_scraping(self):
        """Test user-friendly error creation for scraping errors."""
        error = ScrapingError("ozon.ru", reason="Invalid selector")
        result = create_user_friendly_error(error, "получение данных")
        
        assert result["status"] == "error"
        assert result["error_code"] == "SCRAPING_ERROR"
        assert result["recoverable"] is True
        assert "ozon.ru" in result["message"]

    def test_create_user_friendly_error_database(self):
        """Test user-friendly error creation for database errors."""
        error = DatabaseError("Connection failed", operation="save_product")
        result = create_user_friendly_error(error, "сохранение данных")
        
        assert result["status"] == "error"
        assert result["error_code"] == "DATABASE_ERROR"
        assert result["recoverable"] is True
        assert "базой данных" in result["message"]

    def test_create_user_friendly_error_validation(self):
        """Test user-friendly error creation for validation errors."""
        error = ValidationError("Invalid product code", field="code")
        result = create_user_friendly_error(error, "валидация")
        
        assert result["status"] == "error"
        assert result["error_code"] == "VALIDATION_ERROR"
        assert result["recoverable"] is False
        assert result["retry_suggested"] is False

    def test_log_recovery_attempt(self):
        """Test recovery attempt logging."""
        initial_attempts = error_handler.error_stats["recovery_attempts"]
        initial_successes = error_handler.error_stats["successful_recoveries"]
        
        log_recovery_attempt("test_component", "Test recovery", success=True)
        
        assert error_handler.error_stats["recovery_attempts"] == initial_attempts + 1
        assert error_handler.error_stats["successful_recoveries"] == initial_successes + 1

    def test_error_stats_and_summary(self):
        """Test error statistics and summary generation."""
        # Generate some test errors
        test_errors = [
            ValueError("Error 1"),
            RuntimeError("Error 2"),
            MarketplaceUnavailableError("komus.ru", "Down")
        ]
        
        for i, error in enumerate(test_errors):
            error_handler.log_error(
                error=error,
                category=ErrorCategory.SYSTEM if i < 2 else ErrorCategory.MARKETPLACE,
                severity=ErrorSeverity.MEDIUM,
                component=f"component_{i}",
                details={"marketplace": "komus.ru"} if i == 2 else {}
            )
        
        stats = error_handler.get_error_stats()
        assert stats["total_errors"] == 3
        assert stats["errors_by_category"]["system"] == 2
        assert stats["errors_by_category"]["marketplace"] == 1
        assert stats["marketplace_errors"]["komus.ru"] == 1
        
        recent_errors = error_handler.get_recent_errors(2)
        assert len(recent_errors) == 2
        assert recent_errors[0]["error_type"] == "RuntimeError"

    async def test_database_manager_error_handling(self):
        """Test error handling in DatabaseManager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db_manager = DatabaseManager(db_path)
            
            # Test successful initialization
            await db_manager.init_database()
            
            # Test error handling with invalid data
            invalid_product = {"invalid": "data"}
            
            try:
                await db_manager.save_product(invalid_product)
                assert False, "Should have raised an error"
            except Exception:
                # Error should be logged
                assert error_handler.error_stats["total_errors"] > 0

    async def test_data_processor_error_handling(self):
        """Test error handling in DataProcessor."""
        processor = DataProcessor()
        
        # Test with non-existent file
        result = await processor.load_excel_data("non_existent_file.xlsx")
        assert result == []  # Should return empty list due to error handling
        assert error_handler.error_stats["total_errors"] > 0

    async def test_marketplace_client_error_handling(self):
        """Test error handling in MarketplaceClient."""
        client = MarketplaceClient()
        
        # Test with invalid marketplace
        result = await client.scrape_marketplace("invalid_marketplace", "test query")
        
        # Should return error result due to graceful degradation
        assert result["product_found"] is False
        assert "error" in result
        assert error_handler.error_stats["total_errors"] > 0

    async def test_search_engine_error_handling(self):
        """Test error handling in SearchEngine."""
        search_engine = SearchEngine()
        
        # Test with empty model name
        result = await search_engine.search_product("")
        
        # Should return error result due to error handling
        assert "error" in result
        assert result["total_found"] == 0

    async def test_statistics_generator_error_handling(self):
        """Test error handling in StatisticsGenerator."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db_manager = DatabaseManager(db_path)
            await db_manager.init_database()
            
            stats_generator = StatisticsGenerator(db_manager)
            
            # Test statistics generation (should work without errors)
            stats = await stats_generator.generate_full_statistics()
            assert stats is not None

    def test_error_history_management(self):
        """Test error history size management."""
        handler = ErrorHandler()
        handler.max_history_size = 3
        
        # Add more errors than max size
        for i in range(5):
            handler.log_error(
                error=ValueError(f"Error {i}"),
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.LOW,
                component="test"
            )
        
        # Should only keep the last 3 errors
        assert len(handler.error_history) == 3
        assert handler.error_history[-1].message == "Error 4"

    async def test_graceful_degradation_marketplace_unavailable(self):
        """Test graceful degradation when marketplace is unavailable."""
        @handle_marketplace_errors(graceful_degradation=True)
        async def simulate_marketplace_down():
            raise MarketplaceUnavailableError("komus.ru", "Service maintenance")
        
        result = await simulate_marketplace_down()
        
        # Should return graceful error response
        assert result["marketplace"] == "komus.ru"
        assert result["product_found"] is False
        assert result["recoverable"] is True
        assert "Service maintenance" in result["error"]

    async def test_graceful_degradation_scraping_error(self):
        """Test graceful degradation when scraping fails."""
        @handle_marketplace_errors(graceful_degradation=True)
        async def simulate_scraping_error():
            raise ScrapingError("ozon.ru", reason="Selector not found")
        
        result = await simulate_scraping_error()
        
        # Should return graceful error response
        assert result["marketplace"] == "ozon.ru"
        assert result["product_found"] is False
        assert result["recoverable"] is True
        assert "Selector not found" in result["error"]


async def main():
    """Run all tests."""
    test_instance = TestErrorHandling()
    
    print("🧪 Testing Error Handling Implementation...")
    
    # Run synchronous tests
    sync_tests = [
        "test_error_handler_initialization",
        "test_error_logging",
        "test_marketplace_error_types",
        "test_database_error_types",
        "test_validation_error_types",
        "test_handle_errors_decorator_sync",
        "test_handle_validation_errors_decorator",
        "test_create_user_friendly_error_marketplace",
        "test_create_user_friendly_error_scraping",
        "test_create_user_friendly_error_database",
        "test_create_user_friendly_error_validation",
        "test_log_recovery_attempt",
        "test_error_stats_and_summary",
        "test_error_history_management"
    ]
    
    for test_name in sync_tests:
        test_instance.setup_method()
        try:
            getattr(test_instance, test_name)()
            print(f"{test_name}")
        except Exception as e:
            print(f"{test_name}: {e}")
    
    # Run async tests
    async_tests = [
        "test_handle_errors_decorator_async",
        "test_handle_marketplace_errors_decorator",
        "test_handle_database_errors_decorator",
        "test_database_manager_error_handling",
        "test_data_processor_error_handling",
        "test_marketplace_client_error_handling",
        "test_search_engine_error_handling",
        "test_statistics_generator_error_handling",
        "test_graceful_degradation_marketplace_unavailable",
        "test_graceful_degradation_scraping_error"
    ]
    
    for test_name in async_tests:
        test_instance.setup_method()
        try:
            await getattr(test_instance, test_name)()
            print(f"{test_name}")
        except Exception as e:
            print(f"{test_name}: {e}")
    
    print("\nFinal Error Handler Stats:")
    stats = error_handler.get_error_stats()
    print(f"Total errors logged: {stats['total_errors']}")
    print(f"Recovery attempts: {stats['recovery_attempts']}")
    print(f"Successful recoveries: {stats['successful_recoveries']}")
    
    if stats['recovery_attempts'] > 0:
        recovery_rate = stats['successful_recoveries'] / stats['recovery_attempts'] * 100
        print(f"Recovery rate: {recovery_rate:.1f}%")
    
    print("\nError handling tests completed!")


if __name__ == "__main__":
    asyncio.run(main())