#!/usr/bin/env python3
"""
Direct test for centralized error handling functionality.
Tests the core error handling components by importing the module directly.
"""

import asyncio
import sys
import os
import importlib.util

def load_error_handling_module():
    """Load the error handling module directly."""
    spec = importlib.util.spec_from_file_location(
        "error_handling", 
        "offers_check_marketplaces/error_handling.py"
    )
    error_handling = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(error_handling)
    return error_handling

async def test_error_handling():
    """Test the core error handling functionality."""
    print("🧪 Testing centralized error handling...")
    
    # Load the error handling module
    eh = load_error_handling_module()
    
    # Test 1: Error Handler basic functionality
    print("\n1. Testing ErrorHandler...")
    handler = eh.ErrorHandler()
    
    test_error = ValueError("Test validation error")
    error_info = handler.log_error(
        error=test_error,
        category=eh.ErrorCategory.VALIDATION,
        severity=eh.ErrorSeverity.MEDIUM,
        component="test_component",
        details={"test_field": "test_value"},
        recovery_action="Return default value"
    )
    
    assert error_info.error_type == "ValueError"
    assert error_info.message == "Test validation error"
    assert error_info.category == eh.ErrorCategory.VALIDATION
    assert error_info.component == "test_component"
    print("ErrorHandler basic functionality works")
    
    # Test 2: Error statistics
    print("\n2. Testing error statistics...")
    stats = handler.get_error_stats()
    assert stats["total_errors"] >= 1
    assert "validation" in stats["errors_by_category"]
    assert "test_component" in stats["errors_by_component"]
    print("Error statistics tracking works")
    
    # Test 3: Recent errors
    print("\n3. Testing recent errors...")
    recent = handler.get_recent_errors(5)
    assert len(recent) >= 1
    assert recent[-1]["error_type"] == "ValueError"
    print("Recent errors retrieval works")
    
    # Test 4: Error decorators
    print("\n4. Testing error decorators...")
    
    @eh.handle_errors(
        category=eh.ErrorCategory.SYSTEM,
        severity=eh.ErrorSeverity.LOW,
        component="test_decorator",
        return_on_error="error_handled"
    )
    def test_sync_function():
        raise RuntimeError("Test sync error")
    
    result = test_sync_function()
    assert result == "error_handled"
    print("Synchronous error decorator works")
    
    @eh.handle_errors(
        category=eh.ErrorCategory.NETWORK,
        severity=eh.ErrorSeverity.MEDIUM,
        component="test_async_decorator",
        return_on_error="async_error_handled"
    )
    async def test_async_function():
        raise ConnectionError("Test async error")
    
    async_result = await test_async_function()
    assert async_result == "async_error_handled"
    print("Asynchronous error decorator works")
    
    # Test 5: Marketplace error decorator
    print("\n5. Testing marketplace error decorator...")
    
    @eh.handle_marketplace_errors(
        marketplace="test_marketplace",
        graceful_degradation=True
    )
    async def test_marketplace_function():
        raise eh.MarketplaceUnavailableError("test_marketplace", "Connection timeout")
    
    marketplace_result = await test_marketplace_function()
    assert marketplace_result["marketplace"] == "test_marketplace"
    assert marketplace_result["product_found"] == False
    assert "недоступен" in marketplace_result["error"]
    assert marketplace_result["recoverable"] == True
    print("Marketplace error decorator with graceful degradation works")
    
    # Test 6: Database error decorator with retry
    print("\n6. Testing database error decorator with retry...")
    
    call_count = 0
    
    @eh.handle_database_errors(
        operation="test_db_operation",
        retry_count=2,
        retry_delay=0.1
    )
    async def test_database_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("Database connection failed")
        return "database_success"
    
    db_result = await test_database_function()
    assert db_result == "database_success"
    assert call_count == 3  # Initial call + 2 retries
    print("Database error decorator with retry logic works")
    
    # Test 7: Validation error decorator
    print("\n7. Testing validation error decorator...")
    
    @eh.handle_validation_errors(
        component="test_validator",
        return_default="validation_default"
    )
    def test_validation_function():
        raise eh.ValidationError("Invalid data", field="test_field", value="invalid_value")
    
    validation_result = test_validation_function()
    assert validation_result == "validation_default"
    print("Validation error decorator works")
    
    # Test 8: User-friendly error messages
    print("\n8. Testing user-friendly error messages...")
    
    marketplace_error = eh.MarketplaceUnavailableError("komus.ru", "Connection timeout")
    friendly_error = eh.create_user_friendly_error(marketplace_error)
    
    assert friendly_error["status"] == "error"
    assert friendly_error["error_code"] == "MARKETPLACE_UNAVAILABLE"
    assert "komus.ru" in friendly_error["message"]
    assert friendly_error["recoverable"] == True
    assert friendly_error["retry_suggested"] == True
    print("User-friendly error messages work")
    
    # Test 9: Recovery logging
    print("\n9. Testing recovery logging...")
    
    initial_attempts = eh.error_handler.error_stats["recovery_attempts"]
    initial_successes = eh.error_handler.error_stats["successful_recoveries"]
    
    eh.log_recovery_attempt("test_component", "Test recovery action", success=True)
    
    assert eh.error_handler.error_stats["recovery_attempts"] == initial_attempts + 1
    assert eh.error_handler.error_stats["successful_recoveries"] == initial_successes + 1
    print("Recovery logging works")
    
    # Test 10: Error summary
    print("\n10. Testing error summary...")
    
    summary = eh.get_error_summary()
    assert "total_errors" in summary
    assert "recovery_rate" in summary
    assert "most_common_category" in summary
    assert "recent_errors" in summary
    print("Error summary generation works")
    
    print("\nAll centralized error handling tests passed!")
    
    # Display final statistics
    print("\nFinal Error Statistics:")
    final_stats = eh.error_handler.get_error_stats()
    for key, value in final_stats.items():
        if key not in ["errors_by_category", "errors_by_component", "marketplace_errors"]:
            print(f"  {key}: {value}")
    
    print(f"\n📝 Error Categories:")
    for category, count in final_stats["errors_by_category"].items():
        print(f"  {category}: {count}")
    
    print(f"\nError Components:")
    for component, count in final_stats["errors_by_component"].items():
        print(f"  {component}: {count}")
    
    print("\n✨ Centralized error handling implementation is complete and working!")


if __name__ == "__main__":
    asyncio.run(test_error_handling())