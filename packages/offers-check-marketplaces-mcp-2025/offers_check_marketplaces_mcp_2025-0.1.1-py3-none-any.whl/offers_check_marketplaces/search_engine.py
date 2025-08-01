"""
Поисковый движок для системы сравнения цен на маркетплейсах.

Координирует поиск товаров на множественных маркетплейсах через MCP Playwright,
определяет приоритетные источники и агрегирует результаты поиска.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .models import Product, SearchResult
from .marketplace_client import MarketplaceClient
from .marketplace_config import (
    get_marketplace_by_display_name, 
    get_all_marketplace_names,
    get_marketplace_display_names,
    get_marketplace_config
)
from .error_handling import (
    handle_errors,
    handle_marketplace_errors,
    ErrorCategory,
    ErrorSeverity,
    error_handler,
    log_recovery_attempt,
    MarketplaceUnavailableError,
    ScrapingError
)


logger = logging.getLogger(__name__)


class SearchEngine:
    """
    Поисковый движок для координации поиска товаров на маркетплейсах.
    
    Определяет приоритетные источники из данных продукта, выполняет
    параллельный поиск на нескольких маркетплейсах и агрегирует результаты.
    """

    def __init__(self):
        """Инициализирует поисковый движок."""
        self.marketplace_client = MarketplaceClient()
        self._search_cache = {}  # Кэш результатов поиска
        self._cache_ttl = 300  # TTL кэша в секундах (5 минут)
        self._rate_limiters = {}  # Словарь для rate limiting по маркетплейсам
        self._last_requests = {}  # Время последних запросов

    @handle_errors(
        category=ErrorCategory.SYSTEM,
        severity=ErrorSeverity.MEDIUM,
        component="search_engine",
        return_on_error={
            "query": "",
            "results": [],
            "total_found": 0,
            "search_timestamp": datetime.now().isoformat(),
            "error": "Ошибка поискового движка"
        },
        recovery_action="Возврат пустого результата поиска"
    )
    async def search_product(
        self, 
        model_name: str, 
        marketplaces: Optional[List[str]] = None,
        playwright_tools: Any = None
    ) -> Dict[str, Any]:
        """
        Выполняет поиск товара на указанных маркетплейсах.
        
        Args:
            model_name: Название модели товара для поиска
            marketplaces: Список маркетплейсов для поиска (если None, используются все)
            playwright_tools: Инструменты MCP Playwright (передаются из контекста)
            
        Returns:
            Dict[str, Any]: Агрегированные результаты поиска
        """
        logger.info(f"Начинаем поиск товара: {model_name}")
        
        # Определяем маркетплейсы для поиска
        target_marketplaces = self._determine_target_marketplaces(marketplaces)
        
        if not target_marketplaces:
            log_recovery_attempt(
                component="search_engine",
                action="Не найдены маркетплейсы для поиска",
                success=False
            )
            return {
                "query": model_name,
                "results": [],
                "total_found": 0,
                "search_timestamp": datetime.now().isoformat(),
                "error": "Не найдены маркетплейсы для поиска"
            }

        # Проверяем кэш
        cache_key = self._generate_cache_key(model_name, target_marketplaces)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            logger.info(f"Возвращаем кэшированный результат для: {model_name}")
            log_recovery_attempt(
                component="search_engine",
                action="Использование кэшированного результата",
                success=True
            )
            return cached_result

        # Выполняем параллельный поиск на всех маркетплейсах
        search_results = await self._parallel_marketplace_search(
            model_name, 
            target_marketplaces,
            playwright_tools
        )

        # Агрегируем результаты с расширенной функциональностью
        aggregated_results = await self.aggregate_marketplace_results(
            model_name, 
            search_results,
            include_failed=True
        )

        # Кэшируем результат
        self._cache_result(cache_key, aggregated_results)

        # Логируем успешное завершение
        successful_count = aggregated_results.get('total_found', 0)
        if successful_count > 0:
            log_recovery_attempt(
                component="search_engine",
                action=f"Успешный поиск: найдено {successful_count} результатов",
                success=True
            )

        logger.info(
            f"Поиск завершен для '{model_name}': "
            f"найдено {aggregated_results['total_found']} результатов"
        )

        return aggregated_results

    async def search_product_with_priorities(
        self, 
        product: Product,
        playwright_tools: Any = None
    ) -> Dict[str, Any]:
        """
        Выполняет поиск товара с учетом приоритетных источников из данных продукта.
        
        Args:
            product: Объект продукта с приоритетными источниками
            playwright_tools: Инструменты MCP Playwright
            
        Returns:
            Dict[str, Any]: Результаты поиска с учетом приоритетов
        """
        try:
            # Определяем приоритетные источники
            priority_marketplaces = self._determine_priority_sources(product)
            
            logger.info(
                f"Поиск товара '{product.model_name}' с приоритетами: {priority_marketplaces}"
            )

            # Выполняем поиск с приоритетами
            results = await self.search_product(
                product.model_name,
                priority_marketplaces,
                playwright_tools
            )

            # Добавляем информацию о приоритетах в результат
            results["priority_sources"] = {
                "priority_1": product.priority_1_source,
                "priority_2": product.priority_2_source,
                "resolved_marketplaces": priority_marketplaces
            }

            return results

        except Exception as e:
            logger.error(f"Ошибка при поиске с приоритетами: {str(e)}")
            return {
                "query": product.model_name,
                "results": [],
                "total_found": 0,
                "search_timestamp": datetime.now().isoformat(),
                "error": f"Ошибка поиска с приоритетами: {str(e)}",
                "priority_sources": {
                    "priority_1": product.priority_1_source,
                    "priority_2": product.priority_2_source,
                    "resolved_marketplaces": []
                }
            }

    async def get_marketplace_price(
        self, 
        marketplace: str, 
        model_name: str,
        playwright_tools: Any = None
    ) -> SearchResult:
        """
        Получает цену товара с конкретного маркетплейса с использованием MarketplaceClient.
        
        Args:
            marketplace: Название маркетплейса
            model_name: Название модели товара
            playwright_tools: Инструменты MCP Playwright
            
        Returns:
            SearchResult: Результат поиска на конкретном маркетплейсе
        """
        try:
            logger.info(f"Получаем цену с {marketplace} для товара: {model_name}")
            
            # Преобразуем название маркетплейса в ключ
            marketplace_key = self._resolve_marketplace_key(marketplace)
            if not marketplace_key:
                return SearchResult(
                    marketplace=marketplace,
                    product_found=False,
                    price=None,
                    currency="RUB",
                    availability="unknown",
                    product_url=None,
                    error_message=f"Неизвестный маркетплейс: {marketplace}",
                    search_timestamp=datetime.now()
                )

            # Применяем rate limiting перед запросом
            await self._apply_rate_limiting(marketplace_key)

            # Выполняем поиск через клиент маркетплейсов
            result = await self.marketplace_client.scrape_marketplace(
                marketplace_key,
                model_name,
                playwright_tools
            )

            # Устанавливаем timestamp если его нет
            if not result.search_timestamp:
                result.search_timestamp = datetime.now()

            logger.info(
                f"Результат поиска на {marketplace}: "
                f"найден={result.product_found}, цена={result.price}"
            )

            return result

        except Exception as e:
            logger.error(f"Ошибка при получении цены с {marketplace}: {str(e)}")
            return SearchResult(
                marketplace=marketplace,
                product_found=False,
                price=None,
                currency="RUB",
                availability="error",
                product_url=None,
                error_message=f"Ошибка получения цены: {str(e)}",
                search_timestamp=datetime.now()
            )

    def parse_search_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсит и структурирует сырые результаты поиска.
        
        Args:
            raw_results: Сырые результаты от MCP Playwright
            
        Returns:
            Dict[str, Any]: Структурированные результаты поиска
        """
        try:
            parsed_results = {
                "success": raw_results.get("success", False),
                "marketplace": raw_results.get("marketplace", "unknown"),
                "products": [],
                "total_found": 0,
                "parsing_errors": []
            }

            # Парсим найденные товары
            products_data = raw_results.get("products", [])
            for product_data in products_data:
                try:
                    parsed_product = self._parse_single_product(product_data)
                    if parsed_product:
                        parsed_results["products"].append(parsed_product)
                except Exception as e:
                    parsed_results["parsing_errors"].append(str(e))

            parsed_results["total_found"] = len(parsed_results["products"])

            return parsed_results

        except Exception as e:
            logger.error(f"Ошибка при парсинге результатов поиска: {str(e)}")
            return {
                "success": False,
                "marketplace": "unknown",
                "products": [],
                "total_found": 0,
                "parsing_errors": [str(e)]
            }

    def _determine_target_marketplaces(
        self, 
        marketplaces: Optional[List[str]]
    ) -> List[str]:
        """
        Определяет целевые маркетплейсы для поиска.
        
        Args:
            marketplaces: Список маркетплейсов или None
            
        Returns:
            List[str]: Список ключей маркетплейсов для поиска
        """
        if marketplaces:
            # Преобразуем названия в ключи маркетплейсов
            resolved_keys = []
            for marketplace in marketplaces:
                key = self._resolve_marketplace_key(marketplace)
                if key:
                    resolved_keys.append(key)
            return resolved_keys
        else:
            # Используем все доступные маркетплейсы
            return get_all_marketplace_names()

    def _determine_priority_sources(self, product: Product) -> List[str]:
        """
        Определяет приоритетные источники из данных продукта.
        
        Args:
            product: Объект продукта с приоритетными источниками
            
        Returns:
            List[str]: Список ключей приоритетных маркетплейсов
        """
        priority_sources = []

        # Добавляем приоритет 1
        if product.priority_1_source:
            key = self._resolve_marketplace_key(product.priority_1_source)
            if key:
                priority_sources.append(key)

        # Добавляем приоритет 2
        if product.priority_2_source:
            key = self._resolve_marketplace_key(product.priority_2_source)
            if key and key not in priority_sources:
                priority_sources.append(key)

        # Если приоритетные источники не найдены, используем все доступные
        if not priority_sources:
            logger.warning(
                f"Не найдены приоритетные источники для товара {product.code}, "
                f"используем все маркетплейсы"
            )
            priority_sources = get_all_marketplace_names()

        return priority_sources

    def _resolve_marketplace_key(self, marketplace_name: str) -> Optional[str]:
        """
        Преобразует название маркетплейса в ключ конфигурации.
        
        Args:
            marketplace_name: Название маркетплейса
            
        Returns:
            Optional[str]: Ключ маркетплейса или None
        """
        if not marketplace_name:
            return None

        # Прямое соответствие ключу
        all_keys = get_all_marketplace_names()
        if marketplace_name in all_keys:
            return marketplace_name

        # Поиск по отображаемому названию
        marketplace_key = get_marketplace_by_display_name(marketplace_name)
        if marketplace_key:
            return marketplace_key

        # Поиск по частичному совпадению
        marketplace_lower = marketplace_name.lower()
        display_names = get_marketplace_display_names()
        
        for key, display_name in display_names.items():
            if marketplace_lower in display_name.lower() or display_name.lower() in marketplace_lower:
                return key

        logger.warning(f"Не удалось найти маркетплейс: {marketplace_name}")
        return None

    async def _parallel_marketplace_search(
        self, 
        model_name: str, 
        marketplaces: List[str],
        playwright_tools: Any = None
    ) -> List[SearchResult]:
        """
        Выполняет параллельный поиск на нескольких маркетплейсах с rate limiting.
        
        Args:
            model_name: Название модели товара
            marketplaces: Список ключей маркетплейсов
            playwright_tools: Инструменты MCP Playwright
            
        Returns:
            List[SearchResult]: Список результатов поиска
        """
        # Создаем задачи для параллельного выполнения с rate limiting
        search_tasks = []
        for marketplace in marketplaces:
            # Создаем задачу, которая включает rate limiting
            async def search_with_rate_limit(mp_key: str) -> SearchResult:
                try:
                    # Применяем rate limiting перед запросом
                    await self._apply_rate_limiting(mp_key)
                    
                    # Выполняем поиск через клиент маркетплейсов
                    result = await self.marketplace_client.scrape_marketplace(
                        mp_key, 
                        model_name,
                        playwright_tools
                    )
                    
                    # Устанавливаем timestamp если его нет
                    if not result.search_timestamp:
                        result.search_timestamp = datetime.now()
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Ошибка поиска на {mp_key}: {str(e)}")
                    return SearchResult(
                        marketplace=mp_key,
                        product_found=False,
                        price=None,
                        currency="RUB",
                        availability="error",
                        product_url=None,
                        error_message=str(e),
                        search_timestamp=datetime.now()
                    )
            
            task = search_with_rate_limit(marketplace)
            search_tasks.append(task)

        # Выполняем все задачи параллельно
        try:
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Обрабатываем результаты и исключения
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Критическая ошибка поиска на {marketplaces[i]}: {str(result)}")
                    # Создаем SearchResult с ошибкой
                    error_result = SearchResult(
                        marketplace=marketplaces[i],
                        product_found=False,
                        price=None,
                        currency="RUB",
                        availability="error",
                        product_url=None,
                        error_message=f"Критическая ошибка: {str(result)}",
                        search_timestamp=datetime.now()
                    )
                    processed_results.append(error_result)
                else:
                    processed_results.append(result)

            logger.info(
                f"Параллельный поиск завершен: {len(processed_results)} результатов, "
                f"успешных: {len([r for r in processed_results if r.product_found])}"
            )

            return processed_results

        except Exception as e:
            logger.error(f"Критическая ошибка при параллельном поиске: {str(e)}")
            # Возвращаем результаты с ошибками для всех маркетплейсов
            return [
                SearchResult(
                    marketplace=marketplace,
                    product_found=False,
                    price=None,
                    currency="RUB",
                    availability="error",
                    product_url=None,
                    error_message=f"Критическая ошибка поиска: {str(e)}",
                    search_timestamp=datetime.now()
                )
                for marketplace in marketplaces
            ]

    def _aggregate_search_results(
        self, 
        model_name: str, 
        search_results: List[SearchResult]
    ) -> Dict[str, Any]:
        """
        Агрегирует результаты поиска с разных маркетплейсов.
        
        Args:
            model_name: Название модели товара
            search_results: Список результатов поиска
            
        Returns:
            Dict[str, Any]: Агрегированные результаты
        """
        successful_results = []
        failed_results = []
        total_found = 0

        # Разделяем успешные и неуспешные результаты
        for result in search_results:
            if result.product_found and result.price:
                successful_results.append(result)
                total_found += 1
            else:
                failed_results.append(result)

        # Сортируем успешные результаты по цене
        successful_results.sort(key=lambda x: x.price or float('inf'))

        # Формируем агрегированный результат
        aggregated = {
            "query": model_name,
            "results": [self._search_result_to_dict(r) for r in search_results],
            "successful_results": [self._search_result_to_dict(r) for r in successful_results],
            "failed_results": [self._search_result_to_dict(r) for r in failed_results],
            "total_found": total_found,
            "total_searched": len(search_results),
            "success_rate": (total_found / len(search_results)) * 100 if search_results else 0,
            "search_timestamp": datetime.now().isoformat()
        }

        # Добавляем статистику по ценам
        if successful_results:
            prices = [r.price for r in successful_results if r.price]
            aggregated["price_statistics"] = {
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) / len(prices),
                "price_range": max(prices) - min(prices),
                "cheapest_marketplace": successful_results[0].marketplace,
                "most_expensive_marketplace": successful_results[-1].marketplace
            }

        return aggregated

    def _search_result_to_dict(self, result: SearchResult) -> Dict[str, Any]:
        """
        Преобразует SearchResult в словарь для JSON сериализации.
        
        Args:
            result: Результат поиска
            
        Returns:
            Dict[str, Any]: Словарь с данными результата
        """
        return {
            "marketplace": result.marketplace,
            "product_found": result.product_found,
            "price": result.price,
            "currency": result.currency,
            "availability": result.availability,
            "product_url": result.product_url,
            "error_message": result.error_message,
            "search_timestamp": result.search_timestamp.isoformat() if result.search_timestamp else None
        }

    def _parse_single_product(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Парсит данные одного товара.
        
        Args:
            product_data: Сырые данные товара
            
        Returns:
            Optional[Dict[str, Any]]: Обработанные данные товара или None
        """
        try:
            return {
                "title": product_data.get("title", ""),
                "price": float(product_data.get("price", 0)) if product_data.get("price") else None,
                "availability": product_data.get("availability", "unknown"),
                "url": product_data.get("url", ""),
                "relevance_score": product_data.get("relevance_score", 0)
            }
        except (ValueError, TypeError) as e:
            logger.warning(f"Ошибка при парсинге товара: {str(e)}")
            return None

    def _generate_cache_key(self, model_name: str, marketplaces: List[str]) -> str:
        """
        Генерирует ключ для кэширования результатов поиска.
        
        Args:
            model_name: Название модели товара
            marketplaces: Список маркетплейсов
            
        Returns:
            str: Ключ кэша
        """
        marketplaces_str = "|".join(sorted(marketplaces))
        return f"{model_name}:{marketplaces_str}"

    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Получает результат из кэша, если он не устарел.
        
        Args:
            cache_key: Ключ кэша
            
        Returns:
            Optional[Dict[str, Any]]: Кэшированный результат или None
        """
        if cache_key not in self._search_cache:
            return None

        cached_data = self._search_cache[cache_key]
        cache_time = cached_data.get("cache_time", 0)
        current_time = datetime.now().timestamp()

        # Проверяем, не устарел ли кэш
        if current_time - cache_time > self._cache_ttl:
            del self._search_cache[cache_key]
            return None

        return cached_data.get("result")

    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """
        Сохраняет результат в кэш.
        
        Args:
            cache_key: Ключ кэша
            result: Результат для кэширования
        """
        self._search_cache[cache_key] = {
            "result": result,
            "cache_time": datetime.now().timestamp()
        }

        # Ограничиваем размер кэша
        if len(self._search_cache) > 100:
            # Удаляем самые старые записи
            oldest_keys = sorted(
                self._search_cache.keys(),
                key=lambda k: self._search_cache[k]["cache_time"]
            )[:20]
            for key in oldest_keys:
                del self._search_cache[key]

    def clear_cache(self) -> None:
        """Очищает кэш результатов поиска."""
        self._search_cache.clear()
        logger.info("Кэш результатов поиска очищен")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику кэша.
        
        Returns:
            Dict[str, Any]: Статистика кэша
        """
        current_time = datetime.now().timestamp()
        valid_entries = 0
        expired_entries = 0

        for cached_data in self._search_cache.values():
            cache_time = cached_data.get("cache_time", 0)
            if current_time - cache_time <= self._cache_ttl:
                valid_entries += 1
            else:
                expired_entries += 1

        return {
            "total_entries": len(self._search_cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_ttl_seconds": self._cache_ttl
        }

    async def _apply_rate_limiting(self, marketplace_key: str) -> None:
        """
        Применяет rate limiting для маркетплейса согласно его конфигурации.
        
        Args:
            marketplace_key: Ключ маркетплейса
        """
        try:
            # Получаем конфигурацию маркетплейса
            config = get_marketplace_config(marketplace_key)
            if not config:
                logger.warning(f"Конфигурация для {marketplace_key} не найдена, пропускаем rate limiting")
                return

            rate_limit = config.get("rate_limit", 2.0)
            current_time = time.time()
            last_request_time = self._last_requests.get(marketplace_key, 0)
            
            time_since_last = current_time - last_request_time
            if time_since_last < rate_limit:
                sleep_time = rate_limit - time_since_last
                logger.debug(f"Rate limiting для {marketplace_key}: ждем {sleep_time:.2f} сек")
                await asyncio.sleep(sleep_time)
            
            self._last_requests[marketplace_key] = time.time()

        except Exception as e:
            logger.error(f"Ошибка при применении rate limiting для {marketplace_key}: {str(e)}")
            # В случае ошибки применяем базовую задержку
            await asyncio.sleep(1.0)

    def get_rate_limiting_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику rate limiting.
        
        Returns:
            Dict[str, Any]: Статистика rate limiting
        """
        current_time = time.time()
        stats = {
            "total_marketplaces": len(self._last_requests),
            "last_requests": {},
            "rate_limits": {}
        }

        for marketplace_key, last_request_time in self._last_requests.items():
            config = get_marketplace_config(marketplace_key)
            rate_limit = config.get("rate_limit", 2.0) if config else 2.0
            
            time_since_last = current_time - last_request_time
            can_request_now = time_since_last >= rate_limit
            
            stats["last_requests"][marketplace_key] = {
                "last_request_timestamp": last_request_time,
                "time_since_last_seconds": time_since_last,
                "can_request_now": can_request_now,
                "wait_time_seconds": max(0, rate_limit - time_since_last)
            }
            
            stats["rate_limits"][marketplace_key] = rate_limit

        return stats

    async def aggregate_marketplace_results(
        self, 
        model_name: str,
        individual_results: List[SearchResult],
        include_failed: bool = True
    ) -> Dict[str, Any]:
        """
        Расширенная агрегация результатов поиска с разных маркетплейсов.
        
        Args:
            model_name: Название модели товара
            individual_results: Список результатов поиска с отдельных маркетплейсов
            include_failed: Включать ли неуспешные результаты в агрегацию
            
        Returns:
            Dict[str, Any]: Расширенные агрегированные результаты
        """
        try:
            successful_results = []
            failed_results = []
            error_results = []
            
            # Классифицируем результаты
            for result in individual_results:
                if result.product_found and result.price and result.price > 0:
                    successful_results.append(result)
                elif result.error_message:
                    error_results.append(result)
                else:
                    failed_results.append(result)

            # Сортируем успешные результаты по цене
            successful_results.sort(key=lambda x: x.price or float('inf'))

            # Базовая агрегация
            aggregated = {
                "query": model_name,
                "search_timestamp": datetime.now().isoformat(),
                "total_searched": len(individual_results),
                "total_found": len(successful_results),
                "total_failed": len(failed_results),
                "total_errors": len(error_results),
                "success_rate": (len(successful_results) / len(individual_results)) * 100 if individual_results else 0,
                "results": [self._search_result_to_dict(r) for r in individual_results]
            }

            # Добавляем категоризированные результаты
            aggregated["successful_results"] = [
                self._search_result_to_dict(r) for r in successful_results
            ]
            
            if include_failed:
                aggregated["failed_results"] = [
                    self._search_result_to_dict(r) for r in failed_results
                ]
                aggregated["error_results"] = [
                    self._search_result_to_dict(r) for r in error_results
                ]

            # Расширенная статистика по ценам
            if successful_results:
                prices = [r.price for r in successful_results if r.price]
                price_stats = self._calculate_price_statistics(prices, successful_results)
                aggregated["price_statistics"] = price_stats

            # Статистика по маркетплейсам
            marketplace_stats = self._calculate_marketplace_statistics(individual_results)
            aggregated["marketplace_statistics"] = marketplace_stats

            # Рекомендации на основе результатов
            recommendations = self._generate_recommendations(successful_results, failed_results)
            aggregated["recommendations"] = recommendations

            return aggregated

        except Exception as e:
            logger.error(f"Ошибка при агрегации результатов: {str(e)}")
            return {
                "query": model_name,
                "search_timestamp": datetime.now().isoformat(),
                "error": f"Ошибка агрегации: {str(e)}",
                "results": []
            }

    def _calculate_price_statistics(
        self, 
        prices: List[float], 
        successful_results: List[SearchResult]
    ) -> Dict[str, Any]:
        """
        Вычисляет расширенную статистику по ценам.
        
        Args:
            prices: Список цен
            successful_results: Список успешных результатов поиска
            
        Returns:
            Dict[str, Any]: Статистика по ценам
        """
        if not prices:
            return {}

        sorted_prices = sorted(prices)
        n = len(prices)
        
        # Базовая статистика
        stats = {
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": sum(prices) / len(prices),
            "median_price": sorted_prices[n // 2] if n % 2 == 1 else (sorted_prices[n // 2 - 1] + sorted_prices[n // 2]) / 2,
            "price_range": max(prices) - min(prices),
            "price_variance": sum((p - sum(prices) / len(prices)) ** 2 for p in prices) / len(prices),
            "total_results_with_prices": len(prices)
        }

        # Стандартное отклонение
        stats["price_std_deviation"] = stats["price_variance"] ** 0.5

        # Информация о самых дешевых и дорогих маркетплейсах
        cheapest_result = min(successful_results, key=lambda x: x.price or float('inf'))
        most_expensive_result = max(successful_results, key=lambda x: x.price or 0)
        
        stats["cheapest_marketplace"] = {
            "name": cheapest_result.marketplace,
            "price": cheapest_result.price,
            "url": cheapest_result.product_url,
            "availability": cheapest_result.availability
        }
        
        stats["most_expensive_marketplace"] = {
            "name": most_expensive_result.marketplace,
            "price": most_expensive_result.price,
            "url": most_expensive_result.product_url,
            "availability": most_expensive_result.availability
        }

        # Процентные различия
        if stats["min_price"] > 0:
            stats["max_price_difference_percent"] = ((stats["max_price"] - stats["min_price"]) / stats["min_price"]) * 100

        # Квартили для анализа распределения цен
        if n >= 4:
            stats["price_quartiles"] = {
                "q1": sorted_prices[n // 4],
                "q2": stats["median_price"],
                "q3": sorted_prices[3 * n // 4]
            }

        return stats

    def _calculate_marketplace_statistics(
        self, 
        all_results: List[SearchResult]
    ) -> Dict[str, Any]:
        """
        Вычисляет статистику по маркетплейсам.
        
        Args:
            all_results: Все результаты поиска
            
        Returns:
            Dict[str, Any]: Статистика по маркетплейсам
        """
        marketplace_stats = {}
        
        for result in all_results:
            marketplace = result.marketplace
            if marketplace not in marketplace_stats:
                marketplace_stats[marketplace] = {
                    "total_searches": 0,
                    "successful_searches": 0,
                    "failed_searches": 0,
                    "error_searches": 0,
                    "average_price": None,
                    "prices": [],
                    "availability_status": [],
                    "response_times": []
                }
            
            stats = marketplace_stats[marketplace]
            stats["total_searches"] += 1
            
            if result.product_found and result.price:
                stats["successful_searches"] += 1
                stats["prices"].append(result.price)
            elif result.error_message:
                stats["error_searches"] += 1
            else:
                stats["failed_searches"] += 1
            
            if result.availability:
                stats["availability_status"].append(result.availability)

        # Вычисляем агрегированные метрики для каждого маркетплейса
        for marketplace, stats in marketplace_stats.items():
            if stats["prices"]:
                stats["average_price"] = sum(stats["prices"]) / len(stats["prices"])
                stats["min_price"] = min(stats["prices"])
                stats["max_price"] = max(stats["prices"])
            
            stats["success_rate"] = (stats["successful_searches"] / stats["total_searches"]) * 100 if stats["total_searches"] > 0 else 0
            
            # Удаляем временные списки для чистоты вывода
            del stats["prices"]
            del stats["availability_status"]
            del stats["response_times"]

        return marketplace_stats

    def _generate_recommendations(
        self, 
        successful_results: List[SearchResult],
        failed_results: List[SearchResult]
    ) -> Dict[str, Any]:
        """
        Генерирует рекомендации на основе результатов поиска.
        
        Args:
            successful_results: Успешные результаты поиска
            failed_results: Неуспешные результаты поиска
            
        Returns:
            Dict[str, Any]: Рекомендации
        """
        recommendations = {
            "best_deals": [],
            "reliability_notes": [],
            "search_optimization": []
        }

        # Рекомендации по лучшим предложениям
        if successful_results:
            # Топ-3 самых дешевых предложения
            cheapest_results = sorted(successful_results, key=lambda x: x.price or float('inf'))[:3]
            for i, result in enumerate(cheapest_results):
                recommendations["best_deals"].append({
                    "rank": i + 1,
                    "marketplace": result.marketplace,
                    "price": result.price,
                    "savings_from_most_expensive": None,  # Будет вычислено ниже
                    "url": result.product_url,
                    "availability": result.availability
                })

            # Вычисляем экономию относительно самого дорогого предложения
            if len(successful_results) > 1:
                max_price = max(r.price for r in successful_results if r.price)
                for deal in recommendations["best_deals"]:
                    if deal["price"] and max_price:
                        savings = max_price - deal["price"]
                        savings_percent = (savings / max_price) * 100
                        deal["savings_from_most_expensive"] = {
                            "amount": savings,
                            "percent": savings_percent
                        }

        # Рекомендации по надежности
        total_searched = len(successful_results) + len(failed_results)
        success_rate = (len(successful_results) / total_searched) * 100 if total_searched > 0 else 0
        
        if success_rate < 50:
            recommendations["reliability_notes"].append(
                "Низкий процент успешных результатов. Рекомендуется проверить доступность маркетплейсов."
            )
        elif success_rate > 80:
            recommendations["reliability_notes"].append(
                "Высокий процент успешных результатов. Поиск работает стабильно."
            )

        # Рекомендации по оптимизации поиска
        if len(failed_results) > len(successful_results):
            recommendations["search_optimization"].append(
                "Рассмотрите возможность уточнения поискового запроса или проверки доступности маркетплейсов."
            )

        if successful_results:
            price_range = max(r.price for r in successful_results if r.price) - min(r.price for r in successful_results if r.price)
            avg_price = sum(r.price for r in successful_results if r.price) / len([r for r in successful_results if r.price])
            
            if price_range > avg_price * 0.5:  # Если разброс цен больше 50% от средней цены
                recommendations["search_optimization"].append(
                    "Обнаружен значительный разброс цен между маркетплейсами. Рекомендуется дополнительная проверка."
                )

        return recommendations