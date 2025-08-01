"""
Модуль генерации статистики для системы сравнения цен на маркетплейсах.

Содержит класс StatisticsGenerator для расчета различных метрик и отчетов
по обработанным товарам, включая успешные совпадения, покрытие маркетплейсов,
средние значения и разбивку по категориям.
"""

import aiosqlite
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .models import Statistics
from .database_manager import DatabaseManager
from .error_handling import (
    handle_errors,
    handle_database_errors,
    ErrorCategory,
    ErrorSeverity,
    error_handler,
    log_recovery_attempt
)


logger = logging.getLogger(__name__)


class StatisticsGenerator:
    """
    Генератор статистики для анализа результатов поиска товаров.
    
    Предоставляет методы для расчета различных метрик:
    - Общая статистика по товарам и ценам
    - Успешные совпадения и покрытие маркетплейсов
    - Средние значения и процентные дельты
    - Разбивка по категориям товаров
    - Детальная аналитика по маркетплейсам
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Инициализирует генератор статистики.
        
        Args:
            db_manager: Экземпляр менеджера базы данных
        """
        self.db_manager = db_manager

    @handle_errors(
        category=ErrorCategory.SYSTEM,
        severity=ErrorSeverity.MEDIUM,
        component="statistics_generator",
        recovery_action="Возврат статистики по умолчанию при ошибке"
    )
    async def generate_full_statistics(self) -> Statistics:
        """
        Генерирует полную статистику по всем обработанным товарам.
        
        Включает все основные метрики согласно требованиям:
        - Общее количество товаров (5.1)
        - Количество товаров с успешными совпадениями цен (5.2)
        - Средние процентные дельты цен (5.3)
        - Разбивка по категориям товаров (5.4)
        - Покрытие маркетплейсов (5.5)
        
        Returns:
            Statistics: Объект с полной статистикой
        """
        try:
            logger.info("Начинаем генерацию полной статистики")
            
            # Используем существующий метод из DatabaseManager
            statistics = await self.db_manager.get_statistics()
            
            logger.info(f"Статистика сгенерирована: {statistics.total_products} товаров, "
                       f"{statistics.products_with_prices} с ценами")
            
            return statistics

        except Exception as e:
            logger.error(f"Ошибка генерации полной статистики: {e}")
            raise

    @handle_database_errors(operation="calculate_success_matches", retry_count=2)
    async def calculate_success_matches(self) -> Dict[str, int]:
        """
        Рассчитывает количество успешных совпадений по различным критериям.
        
        Анализирует:
        - Товары с найденными ценами на приоритетных источниках
        - Товары с ценами на нескольких маркетплейсах
        - Товары с полной ценовой информацией
        
        Returns:
            Dict[str, int]: Словарь с метриками успешных совпадений
        """
        try:
            logger.info("Рассчитываем успешные совпадения")
            
            async with self.db_manager._get_connection() as db:
                db.row_factory = aiosqlite.Row
                
                # Товары с ценами на приоритетном источнике 1
                cursor = await db.execute("""
                    SELECT COUNT(DISTINCT p.id) as count
                    FROM products p
                    INNER JOIN prices pr ON p.id = pr.product_id
                    WHERE pr.marketplace = p.priority_1_source 
                    AND pr.price IS NOT NULL AND pr.price > 0
                """)
                priority_1_matches = (await cursor.fetchone())["count"]

                # Товары с ценами на приоритетном источнике 2
                cursor = await db.execute("""
                    SELECT COUNT(DISTINCT p.id) as count
                    FROM products p
                    INNER JOIN prices pr ON p.id = pr.product_id
                    WHERE pr.marketplace = p.priority_2_source 
                    AND pr.price IS NOT NULL AND pr.price > 0
                """)
                priority_2_matches = (await cursor.fetchone())["count"]

                # Товары с ценами на обоих приоритетных источниках
                cursor = await db.execute("""
                    SELECT COUNT(DISTINCT p.id) as count
                    FROM products p
                    WHERE EXISTS (
                        SELECT 1 FROM prices pr1 
                        WHERE pr1.product_id = p.id 
                        AND pr1.marketplace = p.priority_1_source 
                        AND pr1.price IS NOT NULL AND pr1.price > 0
                    )
                    AND EXISTS (
                        SELECT 1 FROM prices pr2 
                        WHERE pr2.product_id = p.id 
                        AND pr2.marketplace = p.priority_2_source 
                        AND pr2.price IS NOT NULL AND pr2.price > 0
                    )
                """)
                both_priorities_matches = (await cursor.fetchone())["count"]

                # Товары с ценами на 3+ маркетплейсах
                cursor = await db.execute("""
                    SELECT COUNT(*) as count
                    FROM (
                        SELECT product_id
                        FROM prices
                        WHERE price IS NOT NULL AND price > 0
                        GROUP BY product_id
                        HAVING COUNT(DISTINCT marketplace) >= 3
                    )
                """)
                multiple_marketplace_matches = (await cursor.fetchone())["count"]

                return {
                    "priority_1_source_matches": priority_1_matches,
                    "priority_2_source_matches": priority_2_matches,
                    "both_priorities_matches": both_priorities_matches,
                    "multiple_marketplace_matches": multiple_marketplace_matches
                }

        except Exception as e:
            logger.error(f"Ошибка расчета успешных совпадений: {e}")
            raise

    @handle_database_errors(operation="calculate_marketplace_coverage", retry_count=2)
    async def calculate_marketplace_coverage(self) -> Dict[str, Dict[str, float]]:
        """
        Рассчитывает детальное покрытие маркетплейсов.
        
        Анализирует покрытие как в абсолютных числах, так и в процентах,
        включая разбивку по категориям товаров.
        
        Returns:
            Dict[str, Dict[str, float]]: Детальная информация о покрытии
        """
        try:
            logger.info("Рассчитываем покрытие маркетплейсов")
            
            async with self.db_manager._get_connection() as db:
                db.row_factory = aiosqlite.Row
                
                # Общее количество товаров
                cursor = await db.execute("SELECT COUNT(*) as total FROM products")
                total_products = (await cursor.fetchone())["total"]

                # Покрытие по маркетплейсам
                cursor = await db.execute("""
                    SELECT marketplace, COUNT(DISTINCT product_id) as count
                    FROM prices
                    WHERE price IS NOT NULL AND price > 0
                    GROUP BY marketplace
                    ORDER BY count DESC
                """)
                marketplace_rows = await cursor.fetchall()

                coverage_data = {}
                for row in marketplace_rows:
                    marketplace = row["marketplace"]
                    count = row["count"]
                    percentage = (count / total_products * 100) if total_products > 0 else 0.0
                    
                    # Покрытие по категориям для каждого маркетплейса
                    cursor = await db.execute("""
                        SELECT p.category, COUNT(DISTINCT p.id) as count
                        FROM products p
                        INNER JOIN prices pr ON p.id = pr.product_id
                        WHERE pr.marketplace = ? AND pr.price IS NOT NULL AND pr.price > 0
                        GROUP BY p.category
                        ORDER BY count DESC
                    """, (marketplace,))
                    category_rows = await cursor.fetchall()
                    
                    category_coverage = {
                        row["category"]: row["count"] for row in category_rows
                    }

                    coverage_data[marketplace] = {
                        "total_products": count,
                        "coverage_percentage": round(percentage, 2),
                        "category_breakdown": category_coverage
                    }

                return coverage_data

        except Exception as e:
            logger.error(f"Ошибка расчета покрытия маркетплейсов: {e}")
            raise

    @handle_database_errors(operation="calculate_average_values", retry_count=2)
    async def calculate_average_values(self) -> Dict[str, float]:
        """
        Рассчитывает различные средние значения по ценам и дельтам.
        
        Включает:
        - Среднюю процентную дельту между ценами
        - Среднюю цену по категориям
        - Среднюю цену по маркетплейсам
        - Медианные значения цен
        
        Returns:
            Dict[str, float]: Словарь со средними значениями
        """
        try:
            logger.info("Рассчитываем средние значения")
            
            async with self.db_manager._get_connection() as db:
                db.row_factory = aiosqlite.Row
                
                # Средняя дельта цен (используем существующий метод)
                average_delta = await self.db_manager._calculate_average_price_delta(db)

                # Средняя цена по всем товарам
                cursor = await db.execute("""
                    SELECT AVG(price) as avg_price
                    FROM prices
                    WHERE price IS NOT NULL AND price > 0
                """)
                overall_avg_price = (await cursor.fetchone())["avg_price"] or 0.0

                # Средняя цена по категориям
                cursor = await db.execute("""
                    SELECT p.category, AVG(pr.price) as avg_price
                    FROM products p
                    INNER JOIN prices pr ON p.id = pr.product_id
                    WHERE pr.price IS NOT NULL AND pr.price > 0
                    GROUP BY p.category
                """)
                category_avg_rows = await cursor.fetchall()
                category_averages = {
                    row["category"]: round(row["avg_price"], 2) 
                    for row in category_avg_rows
                }

                # Средняя цена по маркетплейсам
                cursor = await db.execute("""
                    SELECT marketplace, AVG(price) as avg_price
                    FROM prices
                    WHERE price IS NOT NULL AND price > 0
                    GROUP BY marketplace
                """)
                marketplace_avg_rows = await cursor.fetchall()
                marketplace_averages = {
                    row["marketplace"]: round(row["avg_price"], 2) 
                    for row in marketplace_avg_rows
                }

                # Медианная цена (приблизительная через квантили)
                cursor = await db.execute("""
                    SELECT price
                    FROM prices
                    WHERE price IS NOT NULL AND price > 0
                    ORDER BY price
                """)
                all_prices = [row["price"] for row in await cursor.fetchall()]
                
                median_price = 0.0
                if all_prices:
                    n = len(all_prices)
                    if n % 2 == 0:
                        median_price = (all_prices[n//2 - 1] + all_prices[n//2]) / 2
                    else:
                        median_price = all_prices[n//2]

                return {
                    "average_delta_percent": round(average_delta, 2),
                    "overall_average_price": round(overall_avg_price, 2),
                    "median_price": round(median_price, 2),
                    "category_averages": category_averages,
                    "marketplace_averages": marketplace_averages
                }

        except Exception as e:
            logger.error(f"Ошибка расчета средних значений: {e}")
            raise

    async def get_category_breakdown(self, include_subcategories: bool = False) -> Dict[str, Dict[str, int]]:
        """
        Получает детальную разбивку товаров по категориям.
        
        Args:
            include_subcategories: Включать ли подкатегории в анализ
            
        Returns:
            Dict[str, Dict[str, int]]: Разбивка по категориям с дополнительной информацией
        """
        try:
            logger.info("Получаем разбивку по категориям")
            
            async with self.db_manager._get_connection() as db:
                db.row_factory = aiosqlite.Row
                
                # Основная разбивка по категориям
                cursor = await db.execute("""
                    SELECT category, 
                           COUNT(*) as total_products,
                           COUNT(CASE WHEN pr.price IS NOT NULL THEN 1 END) as products_with_prices
                    FROM products p
                    LEFT JOIN prices pr ON p.id = pr.product_id
                    GROUP BY category
                    ORDER BY total_products DESC
                """)
                category_rows = await cursor.fetchall()

                category_breakdown = {}
                for row in category_rows:
                    category = row["category"]
                    total = row["total_products"]
                    with_prices = row["products_with_prices"]
                    
                    # Процент покрытия ценами для категории
                    coverage_percent = (with_prices / total * 100) if total > 0 else 0.0
                    
                    category_breakdown[category] = {
                        "total_products": total,
                        "products_with_prices": with_prices,
                        "coverage_percentage": round(coverage_percent, 2)
                    }

                return category_breakdown

        except Exception as e:
            logger.error(f"Ошибка получения разбивки по категориям: {e}")
            raise

    async def generate_marketplace_comparison(self) -> Dict[str, Dict[str, float]]:
        """
        Генерирует сравнительный анализ маркетплейсов.
        
        Сравнивает маркетплейсы по:
        - Количеству найденных товаров
        - Средним ценам
        - Ценовым диапазонам
        - Доступности товаров
        
        Returns:
            Dict[str, Dict[str, float]]: Сравнительная таблица маркетплейсов
        """
        try:
            logger.info("Генерируем сравнение маркетплейсов")
            
            async with self.db_manager._get_connection() as db:
                db.row_factory = aiosqlite.Row
                
                # Получаем список всех маркетплейсов
                cursor = await db.execute("""
                    SELECT DISTINCT marketplace
                    FROM prices
                    WHERE price IS NOT NULL
                    ORDER BY marketplace
                """)
                marketplaces = [row["marketplace"] for row in await cursor.fetchall()]

                comparison_data = {}
                for marketplace in marketplaces:
                    # Статистика по маркетплейсу
                    marketplace_stats = await self.db_manager.get_marketplace_statistics(marketplace)
                    
                    # Дополнительные метрики
                    cursor = await db.execute("""
                        SELECT 
                            COUNT(*) as total_listings,
                            COUNT(CASE WHEN availability = 'В наличии' THEN 1 END) as available_count,
                            COUNT(CASE WHEN availability = 'Нет в наличии' THEN 1 END) as unavailable_count
                        FROM prices
                        WHERE marketplace = ?
                    """, (marketplace,))
                    availability_stats = await cursor.fetchone()
                    
                    total_listings = availability_stats["total_listings"]
                    available_percent = (availability_stats["available_count"] / total_listings * 100) if total_listings > 0 else 0.0
                    
                    comparison_data[marketplace] = {
                        "products_count": marketplace_stats["products_count"],
                        "average_price": marketplace_stats["average_price"],
                        "min_price": marketplace_stats["min_price"],
                        "max_price": marketplace_stats["max_price"],
                        "availability_percentage": round(available_percent, 2),
                        "total_listings": total_listings
                    }

                return comparison_data

        except Exception as e:
            logger.error(f"Ошибка генерации сравнения маркетплейсов: {e}")
            raise

    async def get_price_distribution_analysis(self) -> Dict[str, List[Tuple[str, int]]]:
        """
        Анализирует распределение цен по диапазонам.
        
        Создает гистограмму цен для понимания ценовых сегментов
        и распределения товаров по ценовым категориям.
        
        Returns:
            Dict[str, List[Tuple[str, int]]]: Распределение цен по диапазонам
        """
        try:
            logger.info("Анализируем распределение цен")
            
            async with self.db_manager._get_connection() as db:
                db.row_factory = aiosqlite.Row
                
                # Получаем все цены для анализа
                cursor = await db.execute("""
                    SELECT price, marketplace
                    FROM prices
                    WHERE price IS NOT NULL AND price > 0
                    ORDER BY price
                """)
                price_data = await cursor.fetchall()

                if not price_data:
                    return {}

                # Определяем ценовые диапазоны
                prices = [row["price"] for row in price_data]
                min_price = min(prices)
                max_price = max(prices)
                
                # Создаем 10 равных диапазонов
                range_size = (max_price - min_price) / 10
                ranges = []
                for i in range(10):
                    start = min_price + i * range_size
                    end = min_price + (i + 1) * range_size
                    ranges.append((start, end))

                # Распределяем цены по диапазонам
                distribution = {}
                for marketplace in set(row["marketplace"] for row in price_data):
                    marketplace_prices = [row["price"] for row in price_data if row["marketplace"] == marketplace]
                    
                    range_counts = []
                    for i, (start, end) in enumerate(ranges):
                        count = sum(1 for price in marketplace_prices if start <= price < end or (i == 9 and price == end))
                        range_label = f"{start:.0f}-{end:.0f}"
                        range_counts.append((range_label, count))
                    
                    distribution[marketplace] = range_counts

                return distribution

        except Exception as e:
            logger.error(f"Ошибка анализа распределения цен: {e}")
            raise

    async def generate_summary_report(self) -> Dict[str, any]:
        """
        Генерирует итоговый сводный отчет со всеми ключевыми метриками.
        
        Объединяет все виды статистики в единый отчет для представления
        пользователю или экспорта в другие системы.
        
        Returns:
            Dict[str, any]: Полный сводный отчет
        """
        try:
            logger.info("Генерируем сводный отчет")
            
            # Собираем все виды статистики
            full_stats = await self.generate_full_statistics()
            success_matches = await self.calculate_success_matches()
            marketplace_coverage = await self.calculate_marketplace_coverage()
            average_values = await self.calculate_average_values()
            category_breakdown = await self.get_category_breakdown()
            marketplace_comparison = await self.generate_marketplace_comparison()

            summary_report = {
                "report_timestamp": datetime.now().isoformat(),
                "overview": {
                    "total_products": full_stats.total_products,
                    "products_with_prices": full_stats.products_with_prices,
                    "success_rate_percentage": full_stats.success_rate,
                    "average_delta_percent": full_stats.average_delta_percent
                },
                "success_metrics": success_matches,
                "marketplace_coverage": marketplace_coverage,
                "average_values": average_values,
                "category_analysis": category_breakdown,
                "marketplace_comparison": marketplace_comparison,
                "top_categories": full_stats.get_top_categories(),
                "marketplace_coverage_percent": full_stats.get_marketplace_coverage_percent()
            }

            logger.info("Сводный отчет успешно сгенерирован")
            return summary_report

        except Exception as e:
            logger.error(f"Ошибка генерации сводного отчета: {e}")
            raise