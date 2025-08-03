"""
Клиент для взаимодействия с MCP Playwright сервером.

Обеспечивает интеграцию с MCP Playwright для выполнения веб-скрапинга
маркетплейсов и извлечения информации о товарах и ценах.
"""

import asyncio
import logging
import re
import time
from typing import Dict, Optional, Any, List
from urllib.parse import urljoin, urlparse
from html import unescape
from decimal import Decimal, InvalidOperation

from .marketplace_config import get_marketplace_config, get_search_url
from .models import SearchResult
from .error_handling import (
    handle_marketplace_errors,
    MarketplaceUnavailableError,
    ScrapingError,
    ErrorCategory,
    ErrorSeverity,
    error_handler,
    log_recovery_attempt
)


logger = logging.getLogger(__name__)


class MarketplaceClient:
    """
    Клиент для взаимодействия с MCP Playwright сервером.
    
    Координирует веб-скрапинг маркетплейсов через делегирование задач
    MCP Playwright серверу и обрабатывает полученные результаты.
    """

    def __init__(self):
        """Инициализирует клиент маркетплейсов."""
        self._rate_limiters = {}  # Словарь для rate limiting по маркетплейсам
        self._last_requests = {}  # Время последних запросов

    @handle_marketplace_errors(graceful_degradation=True)
    async def scrape_marketplace(
        self, 
        marketplace_key: str, 
        search_query: str,
        playwright_tools: Any = None
    ) -> SearchResult:
        """
        Выполняет скрапинг маркетплейса через MCP Playwright.
        
        Args:
            marketplace_key: Ключ маркетплейса (например, "komus.ru")
            search_query: Поисковый запрос
            playwright_tools: Инструменты MCP Playwright (передаются из контекста)
            
        Returns:
            SearchResult: Результат поиска товара
        """
        # Получаем конфигурацию маркетплейса
        config = get_marketplace_config(marketplace_key)
        if not config:
            raise ScrapingError(
                marketplace=marketplace_key,
                reason=f"Конфигурация для {marketplace_key} не найдена"
            )

        # Применяем rate limiting
        await self._apply_rate_limit(marketplace_key, config.get("rate_limit", 2.0))

        # Формируем URL для поиска
        search_url = get_search_url(marketplace_key, search_query)
        if not search_url:
            raise ScrapingError(
                marketplace=marketplace_key,
                reason="Не удалось сформировать URL для поиска"
            )

        logger.info(f"Начинаем скрапинг {marketplace_key} для запроса: {search_query}")

        # Формируем запрос для MCP Playwright
        playwright_request = self.format_playwright_request(search_url, config)

        try:
            # Здесь должен быть вызов MCP Playwright инструментов
            # В реальной реализации это будет делегировано через MCP
            if playwright_tools:
                # Пример вызова MCP Playwright (будет реализовано в search_engine)
                raw_result = await self._call_playwright_tools(
                    playwright_tools, 
                    playwright_request
                )
            else:
                # Заглушка для тестирования без реального Playwright
                raw_result = await self._mock_scraping_result(marketplace_key, search_query)

            # Проверяем доступность маркетплейса
            if raw_result.get("status") == "unavailable":
                raise MarketplaceUnavailableError(
                    marketplace=marketplace_key,
                    reason=raw_result.get("error", "Маркетплейс недоступен")
                )

            # Извлекаем информацию о товаре из результатов
            result = await self.extract_price_info(marketplace_key, raw_result, config)
            
            # Логируем успешное восстановление, если были проблемы
            if result.product_found:
                log_recovery_attempt(
                    component="marketplace_client",
                    action=f"Успешный скрапинг {marketplace_key}",
                    success=True
                )
            
            return result

        except (MarketplaceUnavailableError, ScrapingError):
            # Перебрасываем специфичные ошибки маркетплейсов
            raise
        except Exception as e:
            # Преобразуем общие ошибки в ScrapingError
            raise ScrapingError(
                marketplace=marketplace_key,
                url=search_url,
                reason=f"Неожиданная ошибка скрапинга: {str(e)}"
            )

    async def extract_price_info(
        self, 
        marketplace_key: str, 
        raw_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> SearchResult:
        """
        Извлекает информацию о цене и товаре из сырых данных скрапинга.
        
        Args:
            marketplace_key: Ключ маркетплейса
            raw_data: Сырые данные от MCP Playwright
            config: Конфигурация маркетплейса
            
        Returns:
            SearchResult: Обработанный результат поиска
        """
        try:
            # Проверяем наличие ошибки в сырых данных
            if raw_data.get("error"):
                return SearchResult(
                    marketplace=marketplace_key,
                    product_found=False,
                    price=None,
                    currency="RUB",
                    availability="error",
                    product_url=None,
                    error_message=raw_data.get("error")
                )

            # Извлекаем HTML контент
            html_content = raw_data.get("html", "")
            page_url = raw_data.get("url", "")

            if not html_content:
                return SearchResult(
                    marketplace=marketplace_key,
                    product_found=False,
                    price=None,
                    currency="RUB",
                    availability="unknown",
                    product_url=page_url,
                    error_message="Пустой HTML контент"
                )

            # Извлекаем цену
            price = self._extract_price_from_html(html_content, config)
            
            # Извлекаем информацию о наличии
            availability = self._extract_availability_from_html(html_content, config)
            
            # Извлекаем ссылку на товар
            product_url = self._extract_product_url_from_html(
                html_content, config, page_url
            )

            # Определяем, найден ли товар
            product_found = price is not None and price > 0

            logger.info(
                f"Извлечена информация с {marketplace_key}: "
                f"цена={price}, наличие={availability}, найден={product_found}"
            )

            return SearchResult(
                marketplace=marketplace_key,
                product_found=product_found,
                price=price,
                currency="RUB",  # По умолчанию рубли для российских маркетплейсов
                availability=availability,
                product_url=product_url
            )

        except Exception as e:
            logger.error(f"Ошибка при извлечении информации с {marketplace_key}: {str(e)}")
            return SearchResult(
                marketplace=marketplace_key,
                product_found=False,
                price=None,
                currency="RUB",
                availability="error",
                product_url=None,
                error_message=f"Ошибка обработки данных: {str(e)}"
            )

    def format_playwright_request(
        self, 
        url: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Формирует запрос для MCP Playwright с корректными параметрами.
        
        Args:
            url: URL для скрапинга
            config: Конфигурация маркетплейса
            
        Returns:
            Dict[str, Any]: Сформированный запрос для MCP Playwright
        """
        return {
            "url": url,
            "selectors": config.get("selectors", {}),
            "options": {
                "timeout": config.get("timeout", 30) * 1000,  # Playwright ожидает миллисекунды
                "user_agent": config.get("user_agent", ""),
                "wait_for_selector": config["selectors"].get("price", ""),
                "wait_timeout": 5000,  # Ждем появления элементов 5 секунд
                "screenshot": False,  # Не делаем скриншоты для экономии ресурсов
                "extract_text": True,  # Извлекаем текст элементов
                "extract_attributes": ["href", "src", "data-price"],  # Полезные атрибуты
            },
            "actions": [
                {
                    "type": "wait_for_load_state",
                    "state": "networkidle"
                },
                {
                    "type": "wait_for_selector", 
                    "selector": config["selectors"].get("price", ""),
                    "timeout": 5000,
                    "required": False
                }
            ]
        }

    async def _apply_rate_limit(self, marketplace_key: str, rate_limit: float):
        """
        Применяет rate limiting для маркетплейса.
        
        Args:
            marketplace_key: Ключ маркетплейса
            rate_limit: Задержка между запросами в секундах
        """
        current_time = time.time()
        last_request_time = self._last_requests.get(marketplace_key, 0)
        
        time_since_last = current_time - last_request_time
        if time_since_last < rate_limit:
            sleep_time = rate_limit - time_since_last
            logger.debug(f"Rate limiting для {marketplace_key}: ждем {sleep_time:.2f} сек")
            await asyncio.sleep(sleep_time)
        
        self._last_requests[marketplace_key] = time.time()

    async def _call_playwright_tools(
        self, 
        playwright_tools: Any, 
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Вызывает инструменты MCP Playwright для выполнения скрапинга.
        
        Args:
            playwright_tools: Инструменты MCP Playwright
            request: Запрос для скрапинга
            
        Returns:
            Dict[str, Any]: Результат скрапинга
        """
        # Здесь будет реальный вызов MCP Playwright инструментов
        # Пока возвращаем заглушку
        return {
            "html": "<html>Mock HTML content</html>",
            "url": request["url"],
            "status": "success"
        }

    async def _mock_scraping_result(
        self, 
        marketplace_key: str, 
        search_query: str
    ) -> Dict[str, Any]:
        """
        Создает мок-результат скрапинга для тестирования.
        
        Args:
            marketplace_key: Ключ маркетплейса
            search_query: Поисковый запрос
            
        Returns:
            Dict[str, Any]: Мок-результат скрапинга
        """
        # Простая заглушка с разными результатами для разных маркетплейсов
        mock_prices = {
            "komus.ru": 1250.50,
            "vseinstrumenti.ru": 1180.00,
            "ozon.ru": 1320.75,
            "wildberries.ru": 1095.25,
            "officemag.ru": 1275.00
        }
        
        price = mock_prices.get(marketplace_key, 1200.00)
        
        mock_html = f"""
        <html>
            <div class="product-item">
                <div class="price-current">{price} ₽</div>
                <div class="availability-status">В наличии</div>
                <a href="/product/123" class="product-link">Товар: {search_query}</a>
                <h3 class="product-title">{search_query}</h3>
            </div>
        </html>
        """
        
        return {
            "html": mock_html,
            "url": f"https://{marketplace_key}/search?q={search_query}",
            "status": "success"
        }

    def _extract_price_from_html(
        self, 
        html_content: str, 
        config: Dict[str, Any]
    ) -> Optional[float]:
        """
        Извлекает цену из HTML контента.
        
        Args:
            html_content: HTML контент страницы
            config: Конфигурация маркетплейса
            
        Returns:
            Optional[float]: Извлеченная цена или None
        """
        try:
            # Получаем селекторы цены
            price_selectors = config["selectors"].get("price", "").split(", ")
            
            for selector in price_selectors:
                if not selector.strip():
                    continue
                    
                # Простой поиск по классу (для мок-данных)
                class_name = selector.replace(".", "").strip()
                pattern = rf'class="{class_name}"[^>]*>([^<]*)'
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                
                for match in matches:
                    # Извлекаем числовое значение цены
                    price_text = match.strip()
                    price_numbers = re.findall(r'[\d\s,\.]+', price_text)
                    
                    if price_numbers:
                        # Очищаем и конвертируем в float
                        price_str = price_numbers[0].replace(' ', '').replace(',', '.')
                        try:
                            return float(price_str)
                        except ValueError:
                            continue
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении цены: {str(e)}")
            return None

    def _extract_availability_from_html(
        self, 
        html_content: str, 
        config: Dict[str, Any]
    ) -> str:
        """
        Извлекает информацию о наличии из HTML контента.
        
        Args:
            html_content: HTML контент страницы
            config: Конфигурация маркетплейса
            
        Returns:
            str: Статус наличия товара
        """
        try:
            # Получаем селекторы наличия
            availability_selectors = config["selectors"].get("availability", "").split(", ")
            
            for selector in availability_selectors:
                if not selector.strip():
                    continue
                    
                # Простой поиск по классу
                class_name = selector.replace(".", "").strip()
                pattern = rf'class="{class_name}"[^>]*>([^<]*)'
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                
                if matches:
                    availability_text = matches[0].strip().lower()
                    
                    # Определяем статус наличия
                    if any(word in availability_text for word in ["в наличии", "есть", "доступен"]):
                        return "в наличии"
                    elif any(word in availability_text for word in ["нет", "отсутствует", "закончился"]):
                        return "нет в наличии"
                    else:
                        return availability_text
            
            return "неизвестно"
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении наличия: {str(e)}")
            return "ошибка"

    def _extract_product_url_from_html(
        self, 
        html_content: str, 
        config: Dict[str, Any],
        base_url: str
    ) -> Optional[str]:
        """
        Извлекает ссылку на товар из HTML контента.
        
        Args:
            html_content: HTML контент страницы
            config: Конфигурация маркетплейса
            base_url: Базовый URL страницы
            
        Returns:
            Optional[str]: Ссылка на товар или None
        """
        try:
            # Получаем селекторы ссылок
            link_selectors = config["selectors"].get("product_link", "").split(", ")
            
            for selector in link_selectors:
                if not selector.strip():
                    continue
                    
                # Поиск href атрибутов
                if "a" in selector:
                    class_name = selector.replace(".", "").replace(" a", "").strip()
                    pattern = rf'class="{class_name}"[^>]*href="([^"]*)"'
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    
                    if matches:
                        href = matches[0].strip()
                        # Формируем полный URL
                        if href.startswith("http"):
                            return href
                        else:
                            parsed_base = urlparse(base_url)
                            base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
                            return urljoin(base_domain, href)
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении ссылки на товар: {str(e)}")
            return None

    def parse_html_response(
        self, 
        html_content: str, 
        marketplace_key: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Парсит HTML ответ от MCP Playwright и извлекает структурированные данные.
        
        Args:
            html_content: HTML контент страницы
            marketplace_key: Ключ маркетплейса
            config: Конфигурация маркетплейса
            
        Returns:
            Dict[str, Any]: Структурированные данные о товарах
        """
        try:
            # Очищаем HTML от лишних символов
            cleaned_html = self._clean_html_content(html_content)
            
            # Извлекаем все товары на странице
            products = self._extract_all_products(cleaned_html, config)
            
            # Фильтруем и ранжируем результаты
            filtered_products = self._filter_and_rank_products(products)
            
            return {
                "marketplace": marketplace_key,
                "products_found": len(filtered_products),
                "products": filtered_products,
                "parsing_success": True,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге HTML для {marketplace_key}: {str(e)}")
            return {
                "marketplace": marketplace_key,
                "products_found": 0,
                "products": [],
                "parsing_success": False,
                "error": f"Ошибка парсинга: {str(e)}"
            }

    def _clean_html_content(self, html_content: str) -> str:
        """
        Очищает HTML контент от лишних символов и нормализует.
        
        Args:
            html_content: Исходный HTML контент
            
        Returns:
            str: Очищенный HTML контент
        """
        try:
            # Декодируем HTML entities
            cleaned = unescape(html_content)
            
            # Удаляем лишние пробелы и переносы строк
            cleaned = re.sub(r'\s+', ' ', cleaned)
            
            # Удаляем комментарии
            cleaned = re.sub(r'<!--.*?-->', '', cleaned, flags=re.DOTALL)
            
            # Удаляем скрипты и стили
            cleaned = re.sub(r'<script.*?</script>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
            cleaned = re.sub(r'<style.*?</style>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
            
            return cleaned.strip()
            
        except Exception as e:
            logger.warning(f"Ошибка при очистке HTML: {str(e)}")
            return html_content

    def _extract_all_products(
        self, 
        html_content: str, 
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Извлекает информацию о всех товарах на странице.
        
        Args:
            html_content: HTML контент страницы
            config: Конфигурация маркетплейса
            
        Returns:
            List[Dict[str, Any]]: Список найденных товаров
        """
        products = []
        
        try:
            # Ищем все блоки товаров
            product_blocks = self._find_product_blocks(html_content, config)
            
            for block in product_blocks:
                product_info = self._extract_product_from_block(block, config)
                if product_info and product_info.get("price"):
                    products.append(product_info)
                    
        except Exception as e:
            logger.error(f"Ошибка при извлечении товаров: {str(e)}")
            
        return products

    def _find_product_blocks(
        self, 
        html_content: str, 
        config: Dict[str, Any]
    ) -> List[str]:
        """
        Находит блоки HTML с информацией о товарах.
        
        Args:
            html_content: HTML контент страницы
            config: Конфигурация маркетплейса
            
        Returns:
            List[str]: Список HTML блоков товаров
        """
        # Общие паттерны для поиска блоков товаров
        product_block_patterns = [
            r'<div[^>]*class="[^"]*product[^"]*"[^>]*>.*?</div>',
            r'<article[^>]*class="[^"]*item[^"]*"[^>]*>.*?</article>',
            r'<li[^>]*class="[^"]*product[^"]*"[^>]*>.*?</li>',
            r'<div[^>]*class="[^"]*card[^"]*"[^>]*>.*?</div>'
        ]
        
        blocks = []
        for pattern in product_block_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            blocks.extend(matches)
            
        return blocks

    def _extract_product_from_block(
        self, 
        block_html: str, 
        config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Извлекает информацию о товаре из HTML блока.
        
        Args:
            block_html: HTML блок товара
            config: Конфигурация маркетплейса
            
        Returns:
            Optional[Dict[str, Any]]: Информация о товаре или None
        """
        try:
            # Извлекаем цену
            price = self._extract_price_from_html(block_html, config)
            if not price:
                return None
                
            # Извлекаем название товара
            title = self._extract_title_from_block(block_html, config)
            
            # Извлекаем наличие
            availability = self._extract_availability_from_html(block_html, config)
            
            # Извлекаем ссылку
            product_url = self._extract_url_from_block(block_html, config)
            
            return {
                "title": title,
                "price": price,
                "availability": availability,
                "url": product_url,
                "relevance_score": self._calculate_relevance_score(title, price)
            }
            
        except Exception as e:
            logger.debug(f"Ошибка при извлечении товара из блока: {str(e)}")
            return None

    def _extract_title_from_block(
        self, 
        block_html: str, 
        config: Dict[str, Any]
    ) -> str:
        """
        Извлекает название товара из HTML блока.
        
        Args:
            block_html: HTML блок товара
            config: Конфигурация маркетплейса
            
        Returns:
            str: Название товара
        """
        try:
            title_selectors = config["selectors"].get("product_title", "").split(", ")
            
            for selector in title_selectors:
                if not selector.strip():
                    continue
                    
                # Поиск по различным тегам
                if "h3" in selector:
                    pattern = r'<h3[^>]*>([^<]*)</h3>'
                elif "." in selector:
                    class_name = selector.replace(".", "").strip()
                    pattern = rf'class="{class_name}"[^>]*>([^<]*)'
                else:
                    continue
                    
                matches = re.findall(pattern, block_html, re.IGNORECASE)
                if matches:
                    return matches[0].strip()
                    
            return "Товар без названия"
            
        except Exception as e:
            logger.debug(f"Ошибка при извлечении названия: {str(e)}")
            return "Неизвестный товар"

    def _extract_url_from_block(
        self, 
        block_html: str, 
        config: Dict[str, Any]
    ) -> Optional[str]:
        """
        Извлекает URL товара из HTML блока.
        
        Args:
            block_html: HTML блок товара
            config: Конфигурация маркетплейса
            
        Returns:
            Optional[str]: URL товара
        """
        try:
            # Ищем любые ссылки в блоке
            href_pattern = r'href="([^"]*)"'
            matches = re.findall(href_pattern, block_html, re.IGNORECASE)
            
            for href in matches:
                # Фильтруем ссылки на товары
                if any(keyword in href.lower() for keyword in ["product", "item", "catalog"]):
                    return href
                    
            # Если не нашли специфичные ссылки, берем первую
            if matches:
                return matches[0]
                
            return None
            
        except Exception as e:
            logger.debug(f"Ошибка при извлечении URL: {str(e)}")
            return None

    def _calculate_relevance_score(self, title: str, price: float) -> float:
        """
        Вычисляет релевантность товара для ранжирования.
        
        Args:
            title: Название товара
            price: Цена товара
            
        Returns:
            float: Оценка релевантности (0-100)
        """
        score = 50.0  # Базовая оценка
        
        # Увеличиваем оценку за наличие цены
        if price and price > 0:
            score += 20.0
            
        # Увеличиваем оценку за длину названия (более подробные названия лучше)
        if title and len(title) > 20:
            score += 15.0
        elif title and len(title) > 10:
            score += 10.0
            
        # Уменьшаем оценку за подозрительно низкие цены
        if price and price < 10:
            score -= 20.0
            
        return min(100.0, max(0.0, score))

    def _filter_and_rank_products(
        self, 
        products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Фильтрует и ранжирует найденные товары.
        
        Args:
            products: Список товаров
            
        Returns:
            List[Dict[str, Any]]: Отфильтрованный и отсортированный список
        """
        # Фильтруем товары с валидными ценами
        valid_products = [
            p for p in products 
            if p.get("price") and p["price"] > 0
        ]
        
        # Сортируем по релевантности
        sorted_products = sorted(
            valid_products,
            key=lambda x: x.get("relevance_score", 0),
            reverse=True
        )
        
        # Возвращаем топ-10 результатов
        return sorted_products[:10]

    def handle_marketplace_unavailable(
        self, 
        marketplace_key: str, 
        error_details: str
    ) -> SearchResult:
        """
        Обрабатывает случаи недоступности маркетплейса.
        
        Args:
            marketplace_key: Ключ маркетплейса
            error_details: Детали ошибки
            
        Returns:
            SearchResult: Результат с информацией о недоступности
        """
        logger.warning(f"Маркетплейс {marketplace_key} недоступен: {error_details}")
        
        # Определяем тип ошибки
        error_type = self._classify_error(error_details)
        
        return SearchResult(
            marketplace=marketplace_key,
            product_found=False,
            price=None,
            currency="RUB",
            availability="недоступен",
            product_url=None,
            error_message=f"Маркетплейс недоступен ({error_type}): {error_details}"
        )

    def _classify_error(self, error_details: str) -> str:
        """
        Классифицирует тип ошибки для лучшего понимания.
        
        Args:
            error_details: Детали ошибки
            
        Returns:
            str: Тип ошибки
        """
        error_lower = error_details.lower()
        
        if any(keyword in error_lower for keyword in ["timeout", "таймаут"]):
            return "таймаут"
        elif any(keyword in error_lower for keyword in ["connection", "соединение"]):
            return "ошибка соединения"
        elif any(keyword in error_lower for keyword in ["404", "not found"]):
            return "страница не найдена"
        elif any(keyword in error_lower for keyword in ["403", "forbidden", "blocked"]):
            return "доступ заблокирован"
        elif any(keyword in error_lower for keyword in ["500", "server error"]):
            return "ошибка сервера"
        else:
            return "неизвестная ошибка"

    def validate_scraping_result(
        self, 
        result: Dict[str, Any], 
        marketplace_key: str
    ) -> bool:
        """
        Валидирует результат скрапинга на корректность.
        
        Args:
            result: Результат скрапинга
            marketplace_key: Ключ маркетплейса
            
        Returns:
            bool: True, если результат валиден
        """
        try:
            # Проверяем обязательные поля
            required_fields = ["html", "url", "status"]
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Отсутствует поле {field} в результате для {marketplace_key}")
                    return False
                    
            # Проверяем статус
            if result.get("status") != "success":
                logger.warning(f"Неуспешный статус скрапинга для {marketplace_key}: {result.get('status')}")
                return False
                
            # Проверяем наличие HTML контента
            html_content = result.get("html", "")
            if not html_content or len(html_content) < 100:
                logger.warning(f"Слишком короткий HTML контент для {marketplace_key}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при валидации результата для {marketplace_key}: {str(e)}")
            return False

    async def retry_scraping_with_backoff(
        self,
        marketplace_key: str,
        search_query: str,
        playwright_tools: Any,
        max_retries: int = 3
    ) -> SearchResult:
        """
        Повторяет скрапинг с экспоненциальной задержкой при ошибках.
        
        Args:
            marketplace_key: Ключ маркетплейса
            search_query: Поисковый запрос
            playwright_tools: Инструменты MCP Playwright
            max_retries: Максимальное количество попыток
            
        Returns:
            SearchResult: Результат скрапинга
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await self.scrape_marketplace(
                    marketplace_key, 
                    search_query, 
                    playwright_tools
                )
                
                # Если результат успешный, возвращаем его
                if result.product_found or not result.error_message:
                    return result
                    
                # Если это последняя попытка, возвращаем результат как есть
                if attempt == max_retries - 1:
                    return result
                    
                last_error = result.error_message
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Попытка {attempt + 1} не удалась для {marketplace_key}: {str(e)}")
                
            # Экспоненциальная задержка
            if attempt < max_retries - 1:
                delay = (2 ** attempt) * 1.0  # 1, 2, 4 секунды
                logger.info(f"Ждем {delay} сек перед повторной попыткой для {marketplace_key}")
                await asyncio.sleep(delay)
        
        # Если все попытки не удались
        return SearchResult(
            marketplace=marketplace_key,
            product_found=False,
            price=None,
            currency="RUB",
            availability="error",
            product_url=None,
            error_message=f"Все попытки скрапинга не удались. Последняя ошибка: {last_error}"
        )