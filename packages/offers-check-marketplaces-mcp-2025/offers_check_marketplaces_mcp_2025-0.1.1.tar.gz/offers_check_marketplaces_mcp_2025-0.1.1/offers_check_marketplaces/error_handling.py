"""
Централизованная система обработки ошибок для offers-check-marketplaces.
"""

import asyncio
import functools
import logging
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional, Union, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    NETWORK = "network"
    PARSING = "parsing"
    DATABASE = "database"
    VALIDATION = "validation"
    MARKETPLACE = "marketplace"
    SYSTEM = "system"
    CONFIGURATION = "configuration"

@dataclass
class ErrorInfo:
    error_type: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    component: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
    traceback_info: Optional[str] = None
    recovery_action: Optional[str] = None

class MarketplaceError(Exception):
    def __init__(self, message: str, marketplace: str = None, error_code: str = None, recoverable: bool = True):
        super().__init__(message)
        self.marketplace = marketplace
        self.error_code = error_code
        self.recoverable = recoverable
        self.timestamp = datetime.now()

class MarketplaceUnavailableError(MarketplaceError):
    def __init__(self, marketplace: str, reason: str = "Unknown"):
        super().__init__(
            f"Маркетплейс {marketplace} недоступен: {reason}",
            marketplace=marketplace,
            error_code="MARKETPLACE_UNAVAILABLE",
            recoverable=True
        )
        self.reason = reason

class ScrapingError(MarketplaceError):
    def __init__(self, marketplace: str, url: str = None, reason: str = "Unknown"):
        super().__init__(
            f"Ошибка скрапинга {marketplace}: {reason}",
            marketplace=marketplace,
            error_code="SCRAPING_ERROR",
            recoverable=True
        )
        self.url = url
        self.reason = reason

class DataProcessingError(Exception):
    def __init__(self, message: str, data_type: str = None, recoverable: bool = False):
        super().__init__(message)
        self.data_type = data_type
        self.recoverable = recoverable
        self.timestamp = datetime.now()

class DatabaseError(Exception):
    def __init__(self, message: str, operation: str = None, recoverable: bool = True):
        super().__init__(message)
        self.operation = operation
        self.recoverable = recoverable
        self.timestamp = datetime.now()

class ValidationError(Exception):
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message)
        self.field = field
        self.value = value
        self.timestamp = datetime.now()

class ErrorHandler:
    def __init__(self):
        self.error_stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_component": {},
            "marketplace_errors": {},
            "recovery_attempts": 0,
            "successful_recoveries": 0
        }
        self.error_history: List[ErrorInfo] = []
        self.max_history_size = 1000

    def log_error(self, error: Exception, category: ErrorCategory, severity: ErrorSeverity, component: str, details: Optional[Dict[str, Any]] = None, recovery_action: Optional[str] = None) -> ErrorInfo:
        error_info = ErrorInfo(
            error_type=type(error).__name__,
            message=str(error),
            category=category,
            severity=severity,
            component=component,
            timestamp=datetime.now(),
            details=details or {},
            traceback_info=traceback.format_exc(),
            recovery_action=recovery_action
        )
        
        self._update_error_stats(error_info)
        self._add_to_history(error_info)
        self._log_by_severity(error_info)
        
        return error_info

    def _update_error_stats(self, error_info: ErrorInfo):
        self.error_stats["total_errors"] += 1
        
        category_key = error_info.category.value
        self.error_stats["errors_by_category"][category_key] = \
            self.error_stats["errors_by_category"].get(category_key, 0) + 1
        
        self.error_stats["errors_by_component"][error_info.component] = \
            self.error_stats["errors_by_component"].get(error_info.component, 0) + 1
        
        if error_info.details and error_info.details.get('marketplace'):
            marketplace = error_info.details['marketplace']
            self.error_stats["marketplace_errors"][marketplace] = \
                self.error_stats["marketplace_errors"].get(marketplace, 0) + 1

    def _add_to_history(self, error_info: ErrorInfo):
        self.error_history.append(error_info)
        
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]

    def _log_by_severity(self, error_info: ErrorInfo):
        log_message = f"[{error_info.component}] {error_info.error_type}: {error_info.message}"
        
        if error_info.details:
            log_message += f" | Детали: {error_info.details}"
        
        if error_info.recovery_action:
            log_message += f" | Восстановление: {error_info.recovery_action}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)

    def get_error_stats(self) -> Dict[str, Any]:
        return {
            **self.error_stats,
            "history_size": len(self.error_history),
            "last_error": self.error_history[-1].timestamp.isoformat() if self.error_history else None
        }

    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        recent = self.error_history[-limit:] if self.error_history else []
        return [
            {
                "error_type": err.error_type,
                "message": err.message,
                "category": err.category.value,
                "severity": err.severity.value,
                "component": err.component,
                "timestamp": err.timestamp.isoformat(),
                "recovery_action": err.recovery_action
            }
            for err in recent
        ]

error_handler = ErrorHandler()

def handle_errors(category: ErrorCategory, severity: ErrorSeverity = ErrorSeverity.MEDIUM, component: str = "unknown", return_on_error: Any = None, recovery_action: str = None, reraise: bool = False):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.log_error(
                    error=e,
                    category=category,
                    severity=severity,
                    component=component,
                    details={"function": func.__name__, "args_count": len(args)},
                    recovery_action=recovery_action
                )
                
                if reraise:
                    raise
                
                return return_on_error
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_handler.log_error(
                    error=e,
                    category=category,
                    severity=severity,
                    component=component,
                    details={"function": func.__name__, "args_count": len(args)},
                    recovery_action=recovery_action
                )
                
                if reraise:
                    raise
                
                return return_on_error
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

def handle_marketplace_errors(marketplace: str = None, graceful_degradation: bool = True, fallback_result: Any = None):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except MarketplaceUnavailableError as e:
                error_handler.log_error(
                    error=e,
                    category=ErrorCategory.MARKETPLACE,
                    severity=ErrorSeverity.MEDIUM,
                    component="marketplace_client",
                    details={
                        "marketplace": e.marketplace,
                        "reason": e.reason,
                        "function": func.__name__
                    },
                    recovery_action="Пропуск недоступного маркетплейса, продолжение с другими"
                )
                
                if graceful_degradation:
                    return fallback_result or {
                        "marketplace": e.marketplace,
                        "product_found": False,
                        "error": f"Маркетплейс недоступен: {e.reason}",
                        "recoverable": True
                    }
                else:
                    raise
                    
            except ScrapingError as e:
                error_handler.log_error(
                    error=e,
                    category=ErrorCategory.MARKETPLACE,
                    severity=ErrorSeverity.MEDIUM,
                    component="marketplace_client",
                    details={
                        "marketplace": e.marketplace,
                        "url": e.url,
                        "reason": e.reason,
                        "function": func.__name__
                    },
                    recovery_action="Возврат пустого результата, продолжение поиска"
                )
                
                if graceful_degradation:
                    return fallback_result or {
                        "marketplace": e.marketplace,
                        "product_found": False,
                        "error": f"Ошибка скрапинга: {e.reason}",
                        "recoverable": True
                    }
                else:
                    raise
                    
            except Exception as e:
                error_handler.log_error(
                    error=e,
                    category=ErrorCategory.MARKETPLACE,
                    severity=ErrorSeverity.HIGH,
                    component="marketplace_client",
                    details={
                        "marketplace": marketplace,
                        "function": func.__name__,
                        "error_type": type(e).__name__
                    },
                    recovery_action="Возврат ошибки, продолжение с другими маркетплейсами"
                )
                
                if graceful_degradation:
                    return fallback_result or {
                        "marketplace": marketplace or "unknown",
                        "product_found": False,
                        "error": f"Неожиданная ошибка: {str(e)}",
                        "recoverable": False
                    }
                else:
                    raise
        
        return wrapper
    
    return decorator

def handle_database_errors(operation: str = "unknown", retry_count: int = 3, retry_delay: float = 1.0):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            current_delay = retry_delay  # Create local copy
            
            for attempt in range(retry_count + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    
                    if attempt < retry_count:
                        error_handler.log_error(
                            error=e,
                            category=ErrorCategory.DATABASE,
                            severity=ErrorSeverity.MEDIUM,
                            component="database_manager",
                            details={
                                "operation": operation,
                                "attempt": attempt + 1,
                                "max_attempts": retry_count + 1,
                                "function": func.__name__
                            },
                            recovery_action=f"Повторная попытка через {current_delay} сек"
                        )
                        
                        await asyncio.sleep(current_delay)
                        current_delay *= 1.5
                    else:
                        error_handler.log_error(
                            error=e,
                            category=ErrorCategory.DATABASE,
                            severity=ErrorSeverity.HIGH,
                            component="database_manager",
                            details={
                                "operation": operation,
                                "final_attempt": True,
                                "total_attempts": retry_count + 1,
                                "function": func.__name__
                            },
                            recovery_action="Все попытки исчерпаны, возврат ошибки"
                        )
                        raise DatabaseError(
                            f"Ошибка БД после {retry_count + 1} попыток: {str(e)}",
                            operation=operation
                        )
            
            if last_error:
                raise last_error
        
        return wrapper
    
    return decorator

def handle_validation_errors(component: str = "validator", return_default: Any = None):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                error_handler.log_error(
                    error=e,
                    category=ErrorCategory.VALIDATION,
                    severity=ErrorSeverity.LOW,
                    component=component,
                    details={
                        "field": e.field,
                        "value": str(e.value) if e.value is not None else None,
                        "function": func.__name__
                    },
                    recovery_action="Возврат значения по умолчанию"
                )
                
                return return_default
            except Exception as e:
                error_handler.log_error(
                    error=e,
                    category=ErrorCategory.VALIDATION,
                    severity=ErrorSeverity.MEDIUM,
                    component=component,
                    details={"function": func.__name__},
                    recovery_action="Возврат значения по умолчанию"
                )
                
                return return_default
        
        return wrapper
    
    return decorator

def create_user_friendly_error(error: Exception, context: str = "операция") -> Dict[str, Any]:
    if isinstance(error, MarketplaceUnavailableError):
        return {
            "status": "error",
            "error_code": "MARKETPLACE_UNAVAILABLE",
            "message": f"Маркетплейс {error.marketplace} временно недоступен",
            "user_message": "Один из маркетплейсов недоступен, но поиск продолжается на других платформах",
            "recoverable": True,
            "retry_suggested": True
        }
    
    elif isinstance(error, ScrapingError):
        return {
            "status": "error",
            "error_code": "SCRAPING_ERROR",
            "message": f"Ошибка получения данных с {error.marketplace}",
            "user_message": "Не удалось получить данные с одного из маркетплейсов, поиск продолжается",
            "recoverable": True,
            "retry_suggested": True
        }
    
    elif isinstance(error, DatabaseError):
        return {
            "status": "error",
            "error_code": "DATABASE_ERROR",
            "message": "Ошибка при работе с базой данных",
            "user_message": "Временная проблема с сохранением данных, попробуйте позже",
            "recoverable": error.recoverable,
            "retry_suggested": True
        }
    
    elif isinstance(error, ValidationError):
        return {
            "status": "error",
            "error_code": "VALIDATION_ERROR",
            "message": f"Ошибка валидации данных: {error.message}",
            "user_message": "Проверьте корректность введенных данных",
            "recoverable": False,
            "retry_suggested": False
        }
    
    elif isinstance(error, DataProcessingError):
        return {
            "status": "error",
            "error_code": "DATA_PROCESSING_ERROR",
            "message": f"Ошибка обработки данных: {error.message}",
            "user_message": "Проблема с обработкой файла данных, проверьте формат",
            "recoverable": error.recoverable,
            "retry_suggested": error.recoverable
        }
    
    else:
        return {
            "status": "error",
            "error_code": "UNKNOWN_ERROR",
            "message": f"Неожиданная ошибка при выполнении {context}",
            "user_message": "Произошла неожиданная ошибка, попробуйте позже",
            "recoverable": False,
            "retry_suggested": True
        }

def log_recovery_attempt(component: str, action: str, success: bool = True):
    error_handler.error_stats["recovery_attempts"] += 1
    
    if success:
        error_handler.error_stats["successful_recoveries"] += 1
        logger.info(f"[{component}] Успешное восстановление: {action}")
    else:
        logger.warning(f"[{component}] Неудачное восстановление: {action}")

def get_error_summary() -> Dict[str, Any]:
    stats = error_handler.get_error_stats()
    recent_errors = error_handler.get_recent_errors(5)
    
    return {
        "total_errors": stats["total_errors"],
        "recovery_rate": (
            stats["successful_recoveries"] / stats["recovery_attempts"] * 100
            if stats["recovery_attempts"] > 0 else 0
        ),
        "most_common_category": max(
            stats["errors_by_category"].items(),
            key=lambda x: x[1],
            default=("none", 0)
        )[0] if stats["errors_by_category"] else "none",
        "most_problematic_component": max(
            stats["errors_by_component"].items(),
            key=lambda x: x[1],
            default=("none", 0)
        )[0] if stats["errors_by_component"] else "none",
        "marketplace_issues": len(stats["marketplace_errors"]),
        "recent_errors": recent_errors
    }
