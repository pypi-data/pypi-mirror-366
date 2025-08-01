"""
Тесты для модуля statistics.py (задача 7.1).

Проверяет функциональность StatisticsGenerator класса,
включая все методы генерации статистики и отчетов.
"""

import asyncio
import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path

# Импорты из нашего модуля
from offers_check_marketplaces.database_manager import DatabaseManager
from offers_check_marketplaces.statistics import StatisticsGenerator
from offers_check_marketplaces.models import Statistics


class TestStatisticsGenerator:
    """Тесты для класса StatisticsGenerator."""

    @pytest.fixture
    async def db_manager(self):
        """Создает временную базу данных для тестов."""
        # Создаем временный файл для базы данных
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_products.db")
        
        db_manager = DatabaseManager(db_path)
        await db_manager.init_database()
        
        # Добавляем тестовые данные
        await self._populate_test_data(db_manager)
        
        yield db_manager
        
        # Очистка после тестов
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)

    async def _populate_test_data(self, db_manager: DatabaseManager):
        """Заполняет базу данных тестовыми данными."""
        # Тестовые продукты
        test_products = [
            {
                "code": 195385.0,
                "model_name": "Полотно техническое БЯЗЬ",
                "category": "Хозтовары и посуда",
                "unit": "м",
                "priority_1_source": "Комус",
                "priority_2_source": "ВсеИнструменты"
            },
            {
                "code": 195386.0,
                "model_name": "Канцелярские товары",
                "category": "Канцтовары",
                "unit": "шт",
                "priority_1_source": "Озон",
                "priority_2_source": "Wildberries"
            },
            {
                "code": 195387.0,
                "model_name": "Инструменты строительные",
                "category": "Инструменты",
                "unit": "шт",
                "priority_1_source": "ВсеИнструменты",
                "priority_2_source": "Комус"
            },
            {
                "code": 195388.0,
                "model_name": "Товары для дома",
                "category": "Хозтовары и посуда",
                "unit": "шт",
                "priority_1_source": "Комус",
                "priority_2_source": "Озон"
            }
        ]

        # Сохраняем продукты
        product_ids = []
        for product_data in test_products:
            product_id = await db_manager.save_product(product_data)
            product_ids.append(product_id)

        # Тестовые цены
        test_prices = [
            # Продукт 1 - цены на 3 маркетплейсах
            {"product_id": product_ids[0], "marketplace": "Комус", "price": 1500.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://komus.ru/1"},
            {"product_id": product_ids[0], "marketplace": "ВсеИнструменты", "price": 1600.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://vseinstrumenti.ru/1"},
            {"product_id": product_ids[0], "marketplace": "Озон", "price": 1450.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://ozon.ru/1"},
            
            # Продукт 2 - цены на 2 маркетплейсах
            {"product_id": product_ids[1], "marketplace": "Озон", "price": 250.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://ozon.ru/2"},
            {"product_id": product_ids[1], "marketplace": "Wildberries", "price": 280.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://wildberries.ru/2"},
            
            # Продукт 3 - цена только на 1 маркетплейсе
            {"product_id": product_ids[2], "marketplace": "ВсеИнструменты", "price": 3500.0, "currency": "RUB", "availability": "В наличии", "product_url": "https://vseinstrumenti.ru/3"},
            
            # Продукт 4 - без цен (для тестирования товаров без цен)
        ]

        # Сохраняем цены
        for price_data in test_prices:
            await db_manager.save_price(price_data["product_id"], price_data)

    @pytest.fixture
    async def stats_generator(self, db_manager):
        """Создает экземпляр StatisticsGenerator для тестов."""
        return StatisticsGenerator(db_manager)

    @pytest.mark.asyncio
    async def test_generate_full_statistics(self, stats_generator):
        """Тест генерации полной статистики (требования 5.1-5.5)."""
        statistics = await stats_generator.generate_full_statistics()
        
        # Проверяем тип возвращаемого объекта
        assert isinstance(statistics, Statistics)
        
        # Требование 5.1: Общее количество товаров
        assert statistics.total_products == 4
        
        # Требование 5.2: Товары с ценами
        assert statistics.products_with_prices == 3  # 3 товара из 4 имеют цены
        
        # Требование 5.3: Средняя дельта должна быть рассчитана
        assert statistics.average_delta_percent >= 0.0
        
        # Требование 5.4: Разбивка по категориям
        assert isinstance(statistics.category_breakdown, dict)
        assert "Хозтовары и посуда" in statistics.category_breakdown
        assert "Канцтовары" in statistics.category_breakdown
        assert "Инструменты" in statistics.category_breakdown
        assert statistics.category_breakdown["Хозтовары и посуда"] == 2
        
        # Требование 5.5: Покрытие маркетплейсов
        assert isinstance(statistics.marketplace_coverage, dict)
        assert "Комус" in statistics.marketplace_coverage
        assert "ВсеИнструменты" in statistics.marketplace_coverage
        assert "Озон" in statistics.marketplace_coverage
        
        # Проверяем процент успешности
        expected_success_rate = (3 / 4) * 100  # 75%
        assert statistics.success_rate == expected_success_rate

    @pytest.mark.asyncio
    async def test_calculate_success_matches(self, stats_generator):
        """Тест расчета успешных совпадений."""
        success_matches = await stats_generator.calculate_success_matches()
        
        assert isinstance(success_matches, dict)
        assert "priority_1_source_matches" in success_matches
        assert "priority_2_source_matches" in success_matches
        assert "both_priorities_matches" in success_matches
        assert "multiple_marketplace_matches" in success_matches
        
        # Проверяем логику подсчета
        assert success_matches["priority_1_source_matches"] >= 0
        assert success_matches["priority_2_source_matches"] >= 0
        assert success_matches["both_priorities_matches"] >= 0
        assert success_matches["multiple_marketplace_matches"] >= 0

    @pytest.mark.asyncio
    async def test_calculate_marketplace_coverage(self, stats_generator):
        """Тест расчета покрытия маркетплейсов."""
        coverage = await stats_generator.calculate_marketplace_coverage()
        
        assert isinstance(coverage, dict)
        
        # Проверяем структуру данных
        for marketplace, data in coverage.items():
            assert isinstance(data, dict)
            assert "total_products" in data
            assert "coverage_percentage" in data
            assert "category_breakdown" in data
            
            assert isinstance(data["total_products"], int)
            assert isinstance(data["coverage_percentage"], float)
            assert isinstance(data["category_breakdown"], dict)
            
            # Процент должен быть от 0 до 100
            assert 0 <= data["coverage_percentage"] <= 100

    @pytest.mark.asyncio
    async def test_calculate_average_values(self, stats_generator):
        """Тест расчета средних значений."""
        averages = await stats_generator.calculate_average_values()
        
        assert isinstance(averages, dict)
        assert "average_delta_percent" in averages
        assert "overall_average_price" in averages
        assert "median_price" in averages
        assert "category_averages" in averages
        assert "marketplace_averages" in averages
        
        # Проверяем типы данных
        assert isinstance(averages["average_delta_percent"], float)
        assert isinstance(averages["overall_average_price"], float)
        assert isinstance(averages["median_price"], float)
        assert isinstance(averages["category_averages"], dict)
        assert isinstance(averages["marketplace_averages"], dict)
        
        # Цены должны быть положительными
        assert averages["overall_average_price"] >= 0
        assert averages["median_price"] >= 0

    @pytest.mark.asyncio
    async def test_get_category_breakdown(self, stats_generator):
        """Тест получения разбивки по категориям."""
        breakdown = await stats_generator.get_category_breakdown()
        
        assert isinstance(breakdown, dict)
        
        # Проверяем структуру данных для каждой категории
        for category, data in breakdown.items():
            assert isinstance(data, dict)
            assert "total_products" in data
            assert "products_with_prices" in data
            assert "coverage_percentage" in data
            
            assert isinstance(data["total_products"], int)
            assert isinstance(data["products_with_prices"], int)
            assert isinstance(data["coverage_percentage"], float)
            
            # Товары с ценами не могут превышать общее количество
            assert data["products_with_prices"] <= data["total_products"]
            
            # Процент покрытия должен быть от 0 до 100
            assert 0 <= data["coverage_percentage"] <= 100

    @pytest.mark.asyncio
    async def test_generate_marketplace_comparison(self, stats_generator):
        """Тест генерации сравнения маркетплейсов."""
        comparison = await stats_generator.generate_marketplace_comparison()
        
        assert isinstance(comparison, dict)
        
        # Проверяем структуру данных для каждого маркетплейса
        for marketplace, data in comparison.items():
            assert isinstance(data, dict)
            assert "products_count" in data
            assert "average_price" in data
            assert "min_price" in data
            assert "max_price" in data
            assert "availability_percentage" in data
            assert "total_listings" in data
            
            # Проверяем типы данных
            assert isinstance(data["products_count"], int)
            assert isinstance(data["average_price"], float)
            assert isinstance(data["min_price"], float)
            assert isinstance(data["max_price"], float)
            assert isinstance(data["availability_percentage"], float)
            assert isinstance(data["total_listings"], int)
            
            # Логические проверки
            assert data["min_price"] <= data["max_price"]
            assert 0 <= data["availability_percentage"] <= 100

    @pytest.mark.asyncio
    async def test_get_price_distribution_analysis(self, stats_generator):
        """Тест анализа распределения цен."""
        distribution = await stats_generator.get_price_distribution_analysis()
        
        assert isinstance(distribution, dict)
        
        # Проверяем структуру данных
        for marketplace, ranges in distribution.items():
            assert isinstance(ranges, list)
            
            # Должно быть 10 диапазонов
            assert len(ranges) == 10
            
            for range_label, count in ranges:
                assert isinstance(range_label, str)
                assert isinstance(count, int)
                assert count >= 0
                
                # Проверяем формат диапазона (число-число)
                assert "-" in range_label

    @pytest.mark.asyncio
    async def test_generate_summary_report(self, stats_generator):
        """Тест генерации сводного отчета."""
        report = await stats_generator.generate_summary_report()
        
        assert isinstance(report, dict)
        
        # Проверяем основные разделы отчета
        required_sections = [
            "report_timestamp",
            "overview",
            "success_metrics",
            "marketplace_coverage",
            "average_values",
            "category_analysis",
            "marketplace_comparison",
            "top_categories",
            "marketplace_coverage_percent"
        ]
        
        for section in required_sections:
            assert section in report
        
        # Проверяем структуру overview
        overview = report["overview"]
        assert "total_products" in overview
        assert "products_with_prices" in overview
        assert "success_rate_percentage" in overview
        assert "average_delta_percent" in overview
        
        # Проверяем timestamp
        assert isinstance(report["report_timestamp"], str)
        
        # Проверяем что timestamp можно распарсить
        datetime.fromisoformat(report["report_timestamp"])

    @pytest.mark.asyncio
    async def test_empty_database(self):
        """Тест работы с пустой базой данных."""
        # Создаем пустую базу данных
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "empty_test.db")
        
        try:
            db_manager = DatabaseManager(db_path)
            await db_manager.init_database()
            
            stats_generator = StatisticsGenerator(db_manager)
            statistics = await stats_generator.generate_full_statistics()
            
            # Проверяем что статистика корректно обрабатывает пустую БД
            assert statistics.total_products == 0
            assert statistics.products_with_prices == 0
            assert statistics.success_rate == 0.0
            assert statistics.average_delta_percent == 0.0
            assert len(statistics.category_breakdown) == 0
            assert len(statistics.marketplace_coverage) == 0
            
        finally:
            # Очистка
            if os.path.exists(db_path):
                os.remove(db_path)
            os.rmdir(temp_dir)

    @pytest.mark.asyncio
    async def test_error_handling(self, stats_generator):
        """Тест обработки ошибок."""
        # Закрываем соединение с базой данных чтобы вызвать ошибку
        original_db_path = stats_generator.db_manager.db_path
        stats_generator.db_manager.db_path = "/invalid/path/database.db"
        
        # Проверяем что ошибки корректно обрабатываются
        with pytest.raises(Exception):
            await stats_generator.generate_full_statistics()
        
        # Восстанавливаем путь
        stats_generator.db_manager.db_path = original_db_path


def run_tests():
    """Запускает все тесты для модуля statistics.py."""
    print("🧪 Запуск тестов для модуля statistics.py (задача 7.1)")
    print("=" * 60)
    
    # Запускаем pytest
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_statistics_task_7_1.py", 
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    # Для прямого запуска файла
    asyncio.run(run_tests())